#!/usr/bin/env python
__all__ = ['Parameters']

import json, copy


class ParametersKeys(object):
    def __init__(self, key, Type='int', val=None, enumerateItems=None, length=1, default=None):
        self.__key = key
        self.__type= Type
        self.__val = val
        self.__length = length
        self.__enumerateItems = enumerateItems
        self.__default = default
        self.__self_check()

    # def __setattr__(self, key, val):
    #     pass

    def __repr__(self):
        string = f'{self.__key}: {self.__val or self.__default}'
        if self.__type == 'enumerate':
            string += f'\n    {self.__enumerateItems}'
        return string


    def get_val(self, debug=False):
        if self.__val is None:
            if debug: print('val is None, set to default')
            if self.__length == 1:
                self.__val =  self.__default
            else:
                self.__val =  [self.__default for _ in range(self.__length)]
        return self.__val

    def reset_val(self, debug=False):
        self.__val = None

    def set_val(self, val, debug=False):
        if self.__type == 'float':
            assert isinstance(val, float) or isinstance(val, int), f'{self.__key} is float, please give float/int'
            val = float(val)
        elif self.__type == 'int':
            assert isinstance(val, int) or isinstance(val, float) and val%1==0.0, f'{self.__key} is int, please give an int'
            val = int(val)
        elif self.__type == 'string':
            assert isinstance(val, str), f'{self.__key} Type is string'
        elif self.__type == 'enumerate':
            assert val in self.__enumerateItems, f'{self.__key} is a enumerate, items: {self.__enumerateItems}'
        else:
            raise ValueError(f'{self.__type} not support')
        self.__val = val


    def __self_check(self):
        assert not '-' in self.__key, '- is not allowed in key'
        if self.__type == 'enumerate':
            assert isinstance(self.__enumerateItems, list) and len(self.__enumerateItems) > 0, 'enumerate must have items'
        default = self.__default
        if self.__type == 'float':
            default = default or 0.
            assert isinstance(default, int) or isinstance(default, float), f'{self.__key}: default should be float'
            default = float(default)
        elif self.__type == 'int':
            default = 0
            assert isinstance(default, int) or isinstance(default, float) and default%1==0.0, f'{self.__key}: default should be int'
        elif self.__type == 'string':
            default = default or ''
            assert isinstance(default, str), f'{self.__key}: default should be int'
        elif self.__type == 'enumerate':
            default = default or self.__enumerateItems[0]
            assert isinstance(default, str) and default in self.__enumerateItems, f'{self.__key}: default should be int'
        self.__default = default
        # array only support int/float
        if self.__length > 1: 
            assert self.__type in ['float', 'int'], 'only float/int can be element of array'


class Parameters(object):
    def __init__(self, param_json=None, debug=False):
        self.__keys_config = {}
        self.__keys_objects= {}
        if param_json is not None:
            try:
                self.load_config(param_json)
            except Exception as e:
                if debug: print(f'param_json is not a config, {e}')
                try:
                    self.load_parameters(param_json)
                except Exception as e:
                    if debug: print(f'param_json is not a values, {e}')
        self.__debug = debug

    def __getattr__(self, key):
        if key[:1+len(self.__class__.__name__)] == f'_{self.__class__.__name__}':
            object.__getattribute__(self, key)
        else:
            assert key in self.__keys_config.keys(), f'{key} no in parameters config, please use add_key to add key'
            return self.__keys_objects[key].get_val(self.__debug)

    def __setattr__(self, key, val):
        if key[:1+len(self.__class__.__name__)] == f'_{self.__class__.__name__}':
            object.__setattr__(self, key, val)
        else:
            assert key in self.__keys_config.keys(), f'{key} no in parameters config, please use add_key to add key'
            self.__keys_objects[key].set_val(val, self.__debug)

    def __repr__(self):
        keys = self.__keys_objects.keys()
        vals = [self.__getattr__(key) if not isinstance(self.__getattr__(key), list) else str(self.__getattr__(key)) for key in keys ]
        keyval = dict(zip(keys, vals))
        return json.dumps(keyval)

    def load_config(self, keys_config):
        if isinstance(keys_config, dict):
            __keys_config = copy.deepcopy(keys_config)
        elif isinstance(keys_config, str):
            with open(keys_config) as fd:
                __keys_config = json.load(fd)
        elif hasattr(keys_config, 'read'):
            __keys_config = json.load(keys_config)
            # self.__keys_objects
        else:
            raise ValueError('param_json only support dict, filename, filehandle')
        # check config
        for key, feature in __keys_config.items():
            Type = feature['type']
            enumerateItems = feature.get('enumerateItems', None)
            length = feature.get('length', 1)
            default = feature.get('default', None)
            self.update_key(key, Type, enumerateItems, length, default)
            # assert Type in ['int', 'float', 'string', 'enumerate'], f'{Type} not supported'
            # assert isinstance(length, int) and length > 0
            # _kobj = ParametersKeys(key, Type, None, enumerateItems = enumerateItems, length=length, default=default)
            # self.__keys_objects.update({key: _kobj})
            # self.__keys_config.update({key: feature})
    # def __check_config(self, keys_config=None, debug=False):

    def dump_config(self, filename=None):
        if filename is None:
            return copy.deepcopy(self.__keys_config)
        else:
            if isinstance(filename, str):
                with open(filename, 'w') as fd:
                    json.dump(self.__keys_config, fd)
            elif hasattr(filename, 'write'):
                json.dump(self.__keys_config, filename)
            else:
                raise ValueError('Please give a correct filename or filehandle')

    def __load_values(self, parameters, debug=False):
        assert isinstance(parameters, dict)
        # self.__keys_objects
        for key, val in parameters.items():
            self.__keys_objects[key].set_val(val, debug)

    def __dump_values(self, debug=False):
        key_values = {}
        for key, key_obj in self.__keys_objects.items():
            key_values[key] = key_obj.get_val(debug)
        return key_values

    def load_parameters(self, parameters_obj):
        if isinstance(parameters_obj, str):
            with open(parameters_obj) as fd:
                parameters_obj = json.load(fd)
        elif hasattr(parameters_obj, 'read'):
            parameters_obj = json.load(parameters_obj)
        else:
            assert isinstance(parameters_obj, dict), 'Please give a valid dict, filename or filehandle'
        self.load_config(parameters_obj['__keys_config'])
        self.__load_values(parameters_obj['__keys_values'])

    def dump_parameters(self, filename=None):
        parameters_obj = {
            '__keys_config': self.__keys_config, 
            '__keys_values': self.__dump_values()
            }
        if filename is None:
            return parameters_obj
        elif isinstance(filename, str):
            with open(filename, 'w') as fd:
                json.dump(parameters_obj, fd)
        elif hasattr(filename, 'write'):
            json.dump(filename, fd)
        else:
            raise ValueError('Please give a valid filename/filehandle')

    def update_key(self, key, Type, enumerateItems= None, length=1, default=None):
        assert Type in ['int', 'float', 'string', 'enumerate'], f'{Type} not supported'
        assert isinstance(length, int) and length > 0
        _kobj = ParametersKeys(key, Type, None, enumerateItems = enumerateItems, length=length, default=default)
        _feature = {'key': key, 'type': Type, 'enumerateItems': enumerateItems, 'length': length, 'default': default}
        self.__keys_objects.update({key: _kobj})
        self.__keys_config.update({key: _feature})

    def reset_key(self, key):
        if key in self.__keys_objects:
            self.__keys_objects[key].reset_val()

    def remove_key(self, key):
        if key in self.__keys_config:
            del self.__keys_config[key]
            if key in self.__keys_objects:
                del self.__keys_objects[key]


def test_protection(obj, cmd):
    print(cmd)
    try:
        eval(cmd)
    except Exception as e:
        print('ERROR', e)


def test():
    param_config = {
        'string': {
            'key': 'string', 
            'type': 'string',
        },
        'int': {
            'key': 'int', 
            'type': 'int', 
            'default': 1.,
        },
        'float':{
            'key': 'float', 
            'type': 'float', 
            'default': 0,
        },
        'enumerate':{
            'key': 'enumerate',
            'type': 'enumerate',
            'enumerateItems': ['1', '2', '3'],
        },
        'ldaU_U':{
            'key': 'ldaU_U',
            'type':'float',
            'length': 10,
            'default': 2,
        }
    }
    try:
        params = Parameters(param_config, debug=True)
    except Exception as e:
        print(e)
        exit()

    
    print(params.string)
    print(params.int)
    print(params.float)
    print(params.enumerate)

    samples = [1, 1., 1.1, 'x', '1', 'STRINGSING', [1,2,]]
    for key in ['string', 'int', 'float', 'enumerate']:
        print(f'\n\n{key}')
        for val in samples:
            print(f'{val}, {type(val)}')
            try:
                params.__setattr__(key, val)
                print('SUCCESS', params.__getattr__(key))
            except Exception as e:
                print('ERROR', e)

    params.update_key('test', 'int', )
    params.update_key('test', 'float', )
    params.update_key('test', 'string', )

    params.update_key('test', 'enumerate', ['x', 'y', 'z'])
    print(params.dump_parameters())
    print(params)

    params.remove_key('test')
    print(params.dump_parameters())
    print(params)

    params.dump_parameters('hello.json')

    print('\n\n\nload:')
    params2 = Parameters('hello.json')
    print('params:', params2.dump_parameters())
    print('config:', params2.dump_config())
    print(params2)

    print(json.dumps(params2.dump_config(), indent=4))

    params2.update_key('-', 'int')
    print(params2)

if __name__ == '__main__':
    test()


