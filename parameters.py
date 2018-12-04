__all__ = ['Parameters']
import six, re, json, copy


class ParametersArray(list):
    def __init__(self):
        pass


class ParametersKeys(object):
    def __init__(self, key, Type='int', val=None, 
                enumItems=None, enumVals=None,
                isArray=False, length=1, 
                default=None, comments='', reference=''):
        self._key = key
        self._type= Type
        self._val = val
        self._enumItems = enumItems
        self._enumVals  = enumVals 
        self._isArray = isArray
        self._length = length
        self._default = default
        self._comments = comments
        self._reference = reference
        self.__self_check()

    @property
    def _length(self):
        if not hasattr(self, '_param_length'):
            self._param_length = 1
        return self._param_length
    
    @_length.setter
    def _length(self, length):
        self._param_length = length

    # def __setattr__(self, key, val):
    #     pass
    def __getattr__(self, key):
        if self._type == 'enum' and key in self._enumItems:
            return key
        return object.__getattribute__(self, key)

    def __repr__(self):
        string = 'key '+self._key+': '+str(self.__get_val())
        if self._type == 'enum':
            string += '\n    enums: '+str(self._enumItems)
        if self._comments != '':
            string += '\n    '+self._comments
        return string

    def __get_val(self, debug=False):
        if self._val is None:
            if debug: print('val is None, set to default')
            self.__set_val_as_default(debug)
        return self._val

    def __dump_output(self):
        if self._type == 'string':
            return self._val
        elif self._type == 'enum':
            if self._enumVals is not None:
                return self._enumVals[self._enumItems.index(self._val)]
            return self._val
        elif self._isArray:
            return ' '.join([json.dumps(_) for _ in self._val])
        else:
            return json.dumps(self._val)

    def __set_val(self, val, debug=False):
        if self._length == 1:
            val = self.__format_val(val)
        else:
            assert isinstance(val, list) and len(val) == self._length, 'Parameters Errror: '+self._key+' Please give '+str(self._length)+' values'
            for i, x in enum(val):
                val[i] = self.__format_val(x)
        self._val = val

    def __reset_val(self, debug=False):
        self.__set_val_as_default(debug)

    def __set_val_as_default(self, debug=False):
        if self._length == 1:
            self._val =  self._default
        else:
            self._val =  [self._default for _ in range(self._length)]

    def __format_val(self, val, debug=False):
        if self._type == 'float':
            assert isinstance(val, float) or isinstance(val, int), 'Parameters Errror: key \"'+str(self._key)+'\" is float, please give float/int'
            val = float(val)
        elif self._type == 'int':
            assert isinstance(val, int) or isinstance(val, float) and val%1==0.0, 'Parameters Errror: key \"'+str(self._key)+'\" is int, please give an int'
            val = int(val)
        elif self._type == 'string':
            assert isinstance(val, six.string_types), 'Parameters Errror: key \"'+str(self._key)+'\" Type is string'
        elif self._type == 'enum':
            assert val in self._enumItems, 'Parameters Errror: key \"'+str(self._key)+'\" is a enum, items: '+str(self._enumItems)
        else:
            raise ValueError(str(self._type)+' not support')
        return val

    def __getitem__(self, key):
        return self._val[key]

    def __setitem__(self, key, val):
        assert self._length > 1, 'Parameters Errror: key \"'+str(self._key)+'\" is not a valid key for Array set'
        assert isinstance(key, int) and 0<=key<self._length, 'Parameters Errror: '+str(key)+' is not a int, or index out of range '+str(self._length)
        val = self.__format_val(val)
        self._val[key] = val

    def __eq__(self, other):
        if isinstance(other, self._class__):
            return self._val == other.__val
        return self._val == other

    def __self_check(self):
        # check key
        assert re.match('^\d|^_', self._key) is None, 'Parameters ERROR: number or _ cannot be first char'
        assert re.sub('\d', '', self._key).replace('_', '').isalpha(), 'Parameters Errror: key \"'+str(self._key)+'\": only letter/number and _ is allowed in key'
        if self._isArray: 
            assert self._type in ['float', 'int', 'bool'], 'Parameters ERROR: only float/int/bool can be element of array'
        if self._type == 'bool':
            self._enumItems = [True, False]
        default = self._default
        if self._type == 'float':
            default = default or 0.
            assert isinstance(default, int) or isinstance(default, float), 'Parameters Errror: key \"'+str(self._key)+'\": default should be float, instead of '+str(default)
            default = float(default)
        elif self._type == 'int':
            default = 0
            assert isinstance(default, int) or isinstance(default, float) and default%1==0.0, 'Parameters Errror: key \"'+str(self._key)+'\": default should be int, instead of '+str(default)
        elif self._type == 'string':
            default = default or ''
            assert isinstance(default, six.string_types), 'Parameters Errror: key \"'+str(self._key)+'\": default should be string, instead of '+str(default)
        elif self._type == 'enum':
            default = default or self._enumItems[0]
            # print(default, type(default), default in self._enumItems)
            assert isinstance(default, six.string_types) and default in self._enumItems, 'Parameters Errror: key \"'+str(self._key)+'\": default should be in '+str(self._enumItems)+', instead of '+str(default)
        elif self._type == 'bool':
            default = self._enumItems[0]
        self._default = default
        self.__set_val_as_default()
        # array only support int/float

    def __get_config(self):
        config_dict = {}
        for key in ['key', 'type', "enumItems", "enumVals", "isArray", "length", "default", "comments", "reference"]:
                config_dict[key] = self.__getattr__('_'+key)
        return config_dict


class Parameters(object):
    def __init__(self, param_json=None, debug=False):
        self.__keys_config = {}
        self.__keys_objects= {}
        if param_json is not None:
            try:
                self.LOAD_CONFIG(param_json)
            except Exception as e:
                if debug: print('param_json is not a config, '+str(e))
                try:
                    self.LOAD_PARAMETERS(param_json)
                except Exception as e:
                    if debug: print('param_json is not a values, '+str(e))
        self.__debug = debug

    def __getattr__(self, key):
        if key[:1+len(self.__class__.__name__)] == '_'+str(self.__class__.__name__):
            object.__getattribute__(self, key)
        else:
            assert key in self.__keys_config.keys(), 'Parameters Errror: '+str(key)+' not in parameters config, please use add_key to add key'
            return self.__keys_objects[key]

    def __setattr__(self, key, val):
        if key[:1+len(self.__class__.__name__)] == '_'+str(self.__class__.__name__):
            object.__setattr__(self, key, val)
        else:
            assert key in self.__keys_config.keys(), 'Parameters Errror: '+str(key)+' no in parameters config, please use add_key to add key'
            self.__keys_objects[key]._ParametersKeys__set_val(val, self.__debug)

    def __repr__(self):
        keyval = dict(zip(self.__keys(), self.__vals()))
        return self.__format_string_parameters(keyval)

    def __format_string_parameters(self, json_obj=None):
        json_obj = json_obj or self.DUMP_PARAMETERS()
        string = json.dumps(json_obj, indent=2)
        string = re.sub('\n\s+(?=\w|])', ' ', string)
        return string

    def LOAD_CONFIG(self, keys_config):
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
            enumItems = feature.get('enumItems', None)
            enumVals = feature.get('enumVals', None)
            isArray = feature.get('isArray', False)
            length = feature.get('length', 1)
            default = feature.get('default', None)
            comments = feature.get('comments', '')
            reference = feature.get('reference', '')
            try:
                self.UPDATE_KEY(key, Type, 
                    enumItems=enumItems, enumVals=enumVals, 
                    isArray=isArray, length=length, 
                    default=default, comments=comments, reference=reference)
            except Exception as e:
                raise e

    def DUMP_CONFIG(self, filename=None):
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

    def LOAD_VALUES(self, parameters, debug=False):
        assert isinstance(parameters, dict)
        # self.__keys_objects
        for key, val in parameters.items():
            self.__keys_objects[key]._ParametersKeys__set_val(val, debug)

    def DUMP_VALUES(self, debug=False):
        key_values = {}
        for key, key_obj in self.__keys_objects.items():
            _val = key_obj._ParametersKeys__get_val(debug)
            if hasattr(_val, 'copy'):
                _val = _val.copy()
            key_values[key] = _val
        return key_values

    def LOAD_PARAMETERS(self, parameters_obj):
        if isinstance(parameters_obj, six.string_types):
            with open(parameters_obj) as fd:
                parameters_obj = json.load(fd)
        elif hasattr(parameters_obj, 'read'):
            parameters_obj = json.load(parameters_obj)
        else:
            assert isinstance(parameters_obj, dict), 'Please give a valid dict, filename or filehandle'
        self.LOAD_CONFIG(parameters_obj['__keys_config'])
        self.LOAD_VALUES(parameters_obj['__keys_values'])

    def DUMP_PARAMETERS(self, filename=None):
        parameters_obj = {
            '__keys_config': self.__keys_config, 
            '__keys_values': self.DUMP_VALUES()
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

    def DUMP_OUTPUT(self, filename=None):
        string = ''
        for key in self.__keys():
            string += key + ' = '+ self.__keys_objects[key]._ParametersKeys__dump_output() + '\n'
        return string

    def UPDATE_KEY(self, key, Type, 
            enumItems= None, enumVals = None,
            isArray=False, length=1, default=None, 
            comments='', reference=''):
        assert Type in ['int', 'float', 'string', 'enum', 'bool'], 'Parameters ERROR: '+str(Type)+' not supported'
        # import pdb; pdb.set_trace();
        if isinstance(length, six.string_types):
            assert length.isdigit(), 'Parameters ERROR: Please give a int string'
            length = int(length)
        assert isinstance(length, int) and length > 0, 'Parameters ERROR: '+key+' :length should be int and > 0'
        if isinstance(default, six.string_types) and Type in ['float', 'int'] \
            and re.match("^\d+?\.\d+?$|\d+", default):
            default = float(default)
        if Type == 'enum':
            if isinstance(enumItems, six.string_types):
                # try to split enumItems with , or | 
                enumItems = re.split('\s*\|\s*|\s*,\s*', enumItems)
            assert isinstance(enumItems, list) and len(enumItems) > 0, 'Parameters Errror: enum must have items'
            if enumVals is not None and isinstance(enumVals, six.string_types):
                enumVals = re.split('\s*\|\s*|\s*,\s*', enumVals)
                assert len(enumVals) == len(enumItems), key+': enumItems and enumVals should have same length'
        if isinstance(isArray, six.string_types):
            if isArray.lower() =='true':
                isArray = True
            elif isArray.lower() == 'false':
                isArray = False
            else:
                raise ValueError('isArray as a string should be true/false')

        _kobj = ParametersKeys(key, Type, 
            enumItems = enumItems, enumVals = enumVals,
            isArray=isArray, length=length, 
            default=default, comments=comments, reference=reference)
        # _feature = {'key': key, 'type': Type, 'enumItems': enumItems, 'length': length, 'default': default, "comments": comments}
        self.__keys_objects.update({key: _kobj})
        self.__keys_config.update({key: _kobj._ParametersKeys__get_config()})

    def RESET_KEY(self, key):
        if key in self.__keys_objects:
            self.__keys_objects[key]._ParametersKeys__reset_val()

    def REMOVE_KEY(self, key):
        if key in self.__keys_config:
            del self.__keys_config[key]
            if key in self.__keys_objects:
                del self.__keys_objects[key]

    def __keys(self):
        return self.__keys_objects.keys()

    def __vals(self):
        return [self.__getattr__(key)._ParametersKeys__get_val() for key in self.__keys()]


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
        'enum':{
            'key': 'enum',
            'type': 'enum',
            'enumItems': ['1', '2', '3'],
        },
        'floatArray':{
            'key': 'ldaU_U',
            'type':'float',
            'length': 10,
            'default': 2,
        },
        'runType':{
            'key': 'runType',
            'type': 'enum',
            'enumItems': ['electron_converge', 'geometry_converge', 'frequency'],
            'default': 'geometry_converge',
        }
    }
    params = Parameters(param_config, debug=True)

    print('\n============================= Run Ordinary Test =============================')
    print(params.string)
    print(params.int)
    print(params.float)
    print(params.enum)
    print(params)

    print('\n========================== Run Type Protection Test =========================')
    samples = [1, 1., 1.1, 'x', '1', 'STRINGSING', [1,2,]]
    for key in ['string', 'int', 'float', 'enum']:
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
    for _type in ['int', 'float', 'string', 'enum']:
        enumItems = None
        if _type == 'enum':
            enumItems = ['x', 'y', 'z']
        _test_params.UPDATE_KEY('test', _type, enumItems = enumItems)
        print('>>> update test to '+str(_type))
        print(_test_params)
    _test_params.REMOVE_KEY('test')
    print('>>> remove test key')
    print(_test_params)

    print('\n============================= Run LOAD Test =============================')
    print(params)
    print('>>> DUMP_PARAMETERS')
    print(params.DUMP_PARAMETERS())
    print('>>> DUMP_PARAMETERS to test.json')
    params.DUMP_PARAMETERS('test.json')
    print('>>> cat test.json')
    import os; os.system('cat test.json')

    print('\n============================= Run LOAD Test =============================')
    print('\n>>> load:')
    _params = Parameters('test.json')
    print('_params == params', _params == params)
    print(params)
    print(_params)
    print('>>> loaded params:')
    print(_params.DUMP_PARAMETERS())
    print('>>> loaded config:')
    print(_params.DUMP_CONFIG())
    print(_params)


    print('\n============================= Run key name Test =============================')
    for _name in ['-', '*', 'test123', '123test', 'test_123', '_test123__', '_ser789*(&']:
        print('test name:  \"'+str(_name)+'\"')
        try:
            _test_params.UPDATE_KEY(_name, 'int')
            print('Success: '+_name)
        except Exception as e:
            print(e)
    print(_test_params)


    print('\n============================= Run Array Test =============================')
    for _type in ['int', 'float', 'string', 'enum']:
        print('>>> UPDATE_KEY Array with length 10: '+_type)
        try:
            _test_params.UPDATE_KEY(_type+'Array', _type, length=10)
        except Exception as e:
            print(e)
        print(_test_params)

    print(_params)
    print(_params.DUMP_CONFIG())
    print('\n=========================== Run Enumerate Test =============================')
    try:
        _params.runType = _params.runType.geometry_converge
    except Exception as e:
        print(e)
    try:
        _params.runType = _params.runType.frequency
    except Exception as e:
        print(e)
    try:
        _params.runType = _params.runType.frequency
    except Exception as e:
        print(e)
    try:
        _params.runType = _params.runType.frequency_analysis
    except Exception as e:
        print(e)
    print(_params)

def parse_primitive_json(json_file):
    with open(json_file) as fd:
        params_dict = json.load(fd)
    # print(json.dumps(params_dict, indent=4))
    params = Parameters()
    for _type, _keys_dict in params_dict.items():
        length = 1
        enumItems = None
        isArray = False
        if 'list_' in _type:
            length = 10
            isArray  = True
            _type = _type.replace('list_', '')
            assert _type in ['int', 'float', 'bool']
        assert _type in ['int', 'float', 'string', 'enum', 'bool'], 'parse error: '+_type+' not support'
        if _type == 'enum':
            enumItems = ['????']
        for _key, _key_config in _keys_dict.items():
            if enumItems is None:
                enumItems = _key_config.get('enumItems', None)
            default = _key_config.get('default', None)
            comments = _key_config.get('comments', '')
            params.UPDATE_KEY(_key, _type, enumItems, isArray, length, default, comments)
    params.DUMP_CONFIG('refined_'+json_file)


def parse_config(json_file):
    params = Parameters(debug=True)
    params.LOAD_CONFIG(json_file)
    params.DUMP_CONFIG('refined_'+json_file)


def parse_parameters(json_file):
    params = Parameters(debug=True)
    params.LOAD_PARAMETERS(json_file)
    params.DUMP_PARAMETERS('refined_'+json_file)
    print(params.DUMP_OUTPUT())
    print(params)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test',  help='run '+str(__file__)+' test', action='store_true')
    parser.add_argument('-pc', '--parse_config', help='parse config json file', nargs=1)
    parser.add_argument('-pr', '--parse_primitive', help='parse primitive json file', nargs=1)
    parser.add_argument('-pp', '--parse_parameters', help='parse parameters json file', nargs=1)
    args = parser.parse_args()
    print(args)
    if args.test:
        test()
    elif args.parse_parameters is not None and len(args.parse_parameters)>0:
        parse_parameters(args.parse_parameters[0])
    elif args.parse_primitive is not None and  len(args.parse_primitive)>0:
        parse_primitive_json(args.parse_primitive[0])
    elif args.parse_config is not None and len(args.parse_config) > 0:
        parse_config(args.parse_config)



