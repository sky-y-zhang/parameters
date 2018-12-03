#!/usr/bin/env python
__all__ = ['Parameters']

import six, re, json, copy


class ParametersArray(list):
    def __init__(self):
        pass


class ParametersKeys(object):
    def __init__(self, key, Type='int', val=None, isBoolean=False, enumerateItems=None, length=1, default=None, comments=''):
        self.__key = key
        self.__type= Type
        self.__val = val
        self.__length = length
        self.__enumerateItems = enumerateItems
        self.__default = default
        self.__self_check()
        self.__comments = comments

    # def __setattr__(self, key, val):
    #     pass
    def __getattr__(self, key):
        if self.__type == 'enumerate' and key in self.__enumerateItems:
            return key
        return object.__getattribute__(self, key)

    def __repr__(self):
        string = 'key '+self.__key+': '+str(self.get_val())
        if self.__type == 'enumerate':
            string += '\n    '+str(self.__enumerateItems)
        if self.__comments != '':
            string += '\n    '+self.__comments
        return string

    def get_val(self, debug=False):
        if self.__val is None:
            if debug: print('val is None, set to default')
            self.set_val_as_default(debug)
        return self.__val

    def set_val(self, val, debug=False):
        if self.__length == 1:
            val = self.format_val(val)
        else:
            assert isinstance(val, list) and len(val) == self.__val, 'Parameters Errror: Please give '+str(self.__length)+' values'
            for i, x in enumerate(val):
                val[i] = self.format_val(x)
        self.__val = val

    def reset_val(self, debug=False):
        self.set_val_as_default(debug)

    def set_val_as_default(self, debug=False):
        if self.__length == 1:
            self.__val =  self.__default
        else:
            self.__val =  [self.__default for _ in range(self.__length)]

    def format_val(self, val, debug=False):
        if self.__type == 'float':
            assert isinstance(val, float) or isinstance(val, int), 'Parameters Errror: key \"'+str(self.__key)+'\" is float, please give float/int'
            val = float(val)
        elif self.__type == 'int':
            assert isinstance(val, int) or isinstance(val, float) and val%1==0.0, 'Parameters Errror: key \"'+str(self.__key)+'\" is int, please give an int'
            val = int(val)
        elif self.__type == 'string':
            assert isinstance(val, six.string_types), 'Parameters Errror: key \"'+str(self.__key)+'\" Type is string'
        elif self.__type == 'enumerate':
            assert val in self.__enumerateItems, 'Parameters Errror: key \"'+str(self.__key)+'\" is a enumerate, items: '+str(self.__enumerateItems)
        else:
            raise ValueError(str(self.__type)+' not support')
        return val

    def __getitem__(self, key):
        return self.__val[key]

    def __setitem__(self, key, val):
        assert self.__length > 1, 'Parameters Errror: key \"'+str(self.__key)+'\" is not a valid key for Array set'
        assert isinstance(key, int) and 0<=key<self.__length, 'Parameters Errror: '+str(key)+' is not a int, or index out of range '+str(self.__length)
        val = self.format_val(val)
        self.__val[key] = val

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__val == other.__val
        return self.__val == other

    def __self_check(self):
        # check key
        assert re.match('^\d', self.__key) is None and re.sub('\d', '', self.__key).replace('_', '').isalpha(), 'Parameters Errror: key \"'+str(self.__key)+'\": only letter/number and _ is allowed in key, number cannot be the start'
        if self.__length > 1: 
            assert self.__type in ['float', 'int'], 'Parameters ERROR: only float/int can be element of array'
        if self.__type == 'enumerate':
            assert isinstance(self.__enumerateItems, list) and len(self.__enumerateItems) > 0, 'Parameters Errror: enumerate must have items'
        default = self.__default
        if self.__type == 'float':
            default = default or 0.
            assert isinstance(default, int) or isinstance(default, float), 'Parameters Errror: key \"'+str(self.__key)+'\": default should be float, instead of '+str(default)
            default = float(default)
        elif self.__type == 'int':
            default = 0
            assert isinstance(default, int) or isinstance(default, float) and default%1==0.0, 'Parameters Errror: key \"'+str(self.__key)+'\": default should be int, instead of '+str(default)
        elif self.__type == 'string':
            default = default or ''
            assert isinstance(default, six.string_types), 'Parameters Errror: key \"'+str(self.__key)+'\": default should be string, instead of '+str(default)
        elif self.__type == 'enumerate':
            default = default or self.__enumerateItems[0]
            print(default, type(default), default in self.__enumerateItems)
            assert isinstance(default, six.string_types) and default in self.__enumerateItems, 'Parameters Errror: key \"'+str(self.__key)+'\": default should be in '+str(self.__enumerateItems)+', instead of '+str(default)
        self.__default = default
        self.set_val_as_default()
        # array only support int/float


class Parameters(object):
    def __init__(self, param_json=None, debug=False):
        self.__keys_config = {}
        self.__keys_objects= {}
        if param_json is not None:
            try:
                self.load_config(param_json)
            except Exception as e:
                if debug: print('param_json is not a config, '+str(e))
                try:
                    self.load_parameters(param_json)
                except Exception as e:
                    if debug: print('param_json is not a values, '+str(e))
        self.__debug = debug

    def __getattr__(self, key):
        if key[:1+len(self.__class__.__name__)] == '_'+str(self.__class__.__name__):
            object.__getattribute__(self, key)
        else:
            assert key in self.__keys_config.keys(), 'Parameters Errror: '+str(key)+' no in parameters config, please use add_key to add key'
            return self.__keys_objects[key]

    def __setattr__(self, key, val):
        if key[:1+len(self.__class__.__name__)] == '_'+str(self.__class__.__name__):
            object.__setattr__(self, key, val)
        else:
            assert key in self.__keys_config.keys(), 'Parameters Errror: '+str(key)+' no in parameters config, please use add_key to add key'
            self.__keys_objects[key].set_val(val, self.__debug)

    def __repr__(self):
        keyval = dict(zip(self.keys(), self.vals()))
        return self.__format_string_parameters(keyval)

    def __format_string_parameters(self, json_obj=None):
        json_obj = json_obj or self.dump_parameters()
        string = json.dumps(json_obj, indent=2)
        string = re.sub('\n\s+(?=\w|])', ' ', string)
        return string

    def load_config(self, keys_config):
        if isinstance(keys_config, dict):
            keys_config = copy.deepcopy(keys_config)
        elif isinstance(keys_config, six.string_types):
            with open(keys_config) as fd:
                keys_config = json.load(fd)
        elif hasattr(keys_config, 'read'):
            keys_config = json.load(keys_config)
        else:
            raise ValueError('param_json only support dict, filename, filehandle')
        # check config
        for key, feature in keys_config.items():
            Type = feature['type']
            enumerateItems = feature.get('enumerateItems', None)
            length = feature.get('length', 1)
            default = feature.get('default', None)
            try:
                self.update_key(key, Type, enumerateItems, length, default)
            except Exception as e:
                print('Load config: update key error '+str(e))

    def dump_config(self, filename=None):
        if filename is None:
            return copy.deepcopy(self.__keys_config)
        else:
            if isinstance(filename, six.string_types):
                with open(filename, 'w') as fd:
                    fd.write(self.__format_string_parameters(self.__keys_config))
            elif hasattr(filename, 'write'):
                filename.write(self.__format_string_parameters(self.__keys_config))
            else:
                raise ValueError('Please give a correct filename or filehandle')

    def load_values(self, parameters, debug=False):
        assert isinstance(parameters, dict)
        # self.__keys_objects
        for key, val in parameters.items():
            self.__keys_objects[key].set_val(val, debug)

    def dump_values(self, debug=False):
        key_values = {}
        for key, key_obj in self.__keys_objects.items():
            _val = key_obj.get_val(debug)
            if hasattr(_val, 'copy'):
                _val = _val.copy()
            key_values[key] = _val
        return key_values

    def load_parameters(self, parameters_obj):
        if isinstance(parameters_obj, six.string_types):
            with open(parameters_obj) as fd:
                parameters_obj = json.load(fd)
        elif hasattr(parameters_obj, 'read'):
            parameters_obj = json.load(parameters_obj)
        else:
            assert isinstance(parameters_obj, dict), 'Please give a valid dict, filename or filehandle'
        self.load_config(parameters_obj['__keys_config'])
        self.load_values(parameters_obj['__keys_values'])

    def dump_parameters(self, filename=None):
        parameters_obj = {
            '__keys_config': self.__keys_config, 
            '__keys_values': self.dump_values()
            }
        if filename is None:
            return parameters_obj
        else:
            parameters_obj = self.__format_string_parameters(parameters_obj)
        if isinstance(filename, six.string_types):
            with open(filename, 'w') as fd:
                fd.write(parameters_obj)
        elif hasattr(filename, 'write'):
            filename.write(parameters_obj)
        else:
            raise ValueError('Please give a valid filename/filehandle')

    def update_key(self, key, Type, enumerateItems= None, length=1, default=None):
        assert Type in ['int', 'float', 'string', 'enumerate'], 'Parameters Errror: '+str(Type)+' not supported'
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

    def keys(self):
        return self.__keys_objects.keys()

    def vals(self):
        return [self.__getattr__(key).get_val() for key in self.keys()]


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
        'floatArray':{
            'key': 'ldaU_U',
            'type':'float',
            'length': 10,
            'default': 2,
        },
        'runType':{
            'key': 'runType',
            'type': 'enumerate',
            'enumerateItems': ['electron_converge', 'geometry_converge', 'frequency'],
            'default': 'geometry_converge',
        }
    }
    params = Parameters(param_config, debug=True)

    print('\n============================= Run Ordinary Test =============================')
    print(params.string)
    print(params.int)
    print(params.float)
    print(params.enumerate)
    print(params)

    print('\n========================== Run Type Protection Test =========================')
    samples = [1, 1., 1.1, 'x', '1', 'STRINGSING', [1,2,]]
    for key in ['string', 'int', 'float', 'enumerate']:
        print(str(key)+'\n')
        for val in samples:
            print('>>> set '+str(key)+' as '+str(val)+', '+str(type(val)))
            try:
                params.__setattr__(key, val)
                print('SUCCESS, '+str(params.__getattr__(key)))
            except Exception as e:
                print(e)
            print('')
        print('\n\n')

    print('\n========================= Run update/remove Test =============================')
    _test_params = Parameters()
    for _type in ['int', 'float', 'string', 'enumerate']:
        enumerateItems = None
        if _type == 'enumerate':
            enumerateItems = ['x', 'y', 'z']
        _test_params.update_key('test', _type, enumerateItems = enumerateItems)
        print('>>> update test to '+str(_type))
        print(_test_params)
    _test_params.remove_key('test')
    print('>>> remove test key')
    print(_test_params)

    print('\n============================= Run LOAD Test =============================')
    print(params)
    print('>>> dump_parameters')
    print(params.dump_parameters())
    print('>>> dump_parameters to test.json')
    params.dump_parameters('test.json')
    print('>>> cat test.json')
    import os; os.system('cat test.json')

    print('\n============================= Run LOAD Test =============================')
    print('\n>>> load:')
    params2 = Parameters('test.json')
    print('params2 == params', params2 == params)
    print(params)
    print(params2)
    print('>>> loaded params:')
    print(params2.dump_parameters())
    print('>>> loaded config:')
    print(params2.dump_config())
    print(params2)


    print('\n============================= Run key name Test =============================')
    for _name in ['-', '*', 'test123', '123test', 'test_123', '_test123__', '_ser789*(&']:
        print('test name:  \"'+str(_name)+'\"')
        try:
            _test_params.update_key(_name, 'int')
            print('Success: '+_name)
        except Exception as e:
            print(e)
    print(_test_params)


    print('\n============================= Run Array Test =============================')
    for _type in ['int', 'float', 'string', 'enumerate']:
        print('>>> update_key Array with length 10: '+_type)
        try:
            _test_params.update_key(_type+'Array', _type, length=10)
        except Exception as e:
            print(e)
        print(_test_params)

    print(params2)
    print(params2.dump_config())
    print('\n=========================== Run Enumerate Test =============================')
    try:
        params2.runType = params2.runType.geometry_converge
    except Exception as e:
        print(e)
    try:
        params2.runType = params2.runType.frequency
    except Exception as e:
        print(e)
    try:
        params2.runType = params2.runType.frequency
    except Exception as e:
        print(e)
    try:
        params2.runType = params2.runType.frequency_analysis
    except Exception as e:
        print(e)
    print(params2)

def parse_json(json_file):
    with open(json_file) as fd:
        params_dict = json.load(fd)
    print(json.dumps(params_dict, indent=4))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test',  help='run '+str(__file__)+' test', action='store_true')
    parser.add_argument('-p', '--parse', help='parse json file', nargs=1)
    args = parser.parse_args()
    if args.test:
        test()
    else:
        parse_json(args.parse[0])


