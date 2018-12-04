# paraparser --- parameters parser

Parameters is design for large program with massive parameters. It supports integer, float, bool, string and enumerate(enum) types. Array is supported for bool, integer and float. For enum type, customized value can be set as well. Data type is protected. And load/dump of parameters/config is available.

## Get instance

You can get an emptry instance, or load from dict/filename/filehandler
```python
params = paraparser.Parameters()
params = paraparser.Parameters(paramters_dict)
params = paraparser.Parameters(parameter_json)
```

## Load config/parameters
After the parameter instance is generated, you can load from a dict/file as well.
```python
params.LOAD_CONFIG(config_file)
params.LOAD_PARAMETERS(parameters_file)
```
You can check parameters.json.sample & config.json.sample for details of parameters/config. 

## update/remove key
Key can be updated/removed, val can be set/reset

```python
>>> params.UPDATE_KEY('test_key', 'int', default=0)
>>> params
{"test_key": 0}
>>> params.test_key = 1
>>> params
{"test_key": 1}
>>> params.test_key
1
>>> params.REMOVE_KEY('test_key')
>>> params.RESET_KEY('test_key')
>>> params
{"test_key": 0}
```

## Special Types

### Array
An integer/float/bool array could be initiate with
```python
>>> params.UPDATE_KEY('test_key', 'int', isArray=True, length=10, default=0)
>>> params
{"test_key": "[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"}
>>> params.UPDATE_KEY('test_key', 'float', isArray=True, length=6, default=0)
>>> params
{"test_key": "[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"}
```

### Enumerate
We highly improved enum type
```python
>>> params.UPDATE_KEY('test_key', 'enum', enumItems=['x1', 'x2', 'x3'], default='x1')
>>> params
{
  "test_key": "x1"
}
>>> params.test_key 
key test_key: x1
    enums: ['x1', 'x2', 'x3']
```
You can customize enuemrate enumerate values with enumVals, which is really useful when cooperating with old programs. 
```python
>>> params.UPDATE_KEY('test_key', 'enum', enumItems=['x1', 'x2', 'x3'], enumVals=['-1', '2', '5'], default='x1')
>>> params
{
  "test_key": "x1"
}
>>> print(params.DUMP_OUTPUT())
test_key = -1

```

## Type Protection
Type is protected within paraparser, e.g.
```python
>>> params.UPDATE_KEY('test_key', 'enum', enumItems=['x1', 'x2', 'x3'], enumVals=['-1', '2', '5'], default='x1')
>>> params
{
  "test_key": "x1"
}
>>> params.test_key = 'x22'
AssertionError: Parameters Errror: key "test_key" is a enum, items: ['x1', 'x2', 'x3']
```
And the same for other types. 


## Output

A beautiful output is available with the instance or use the print function
```python
>>> print(params)
{
  "string": "STRINGSING",
  "int": 1,
  "float": 1.1,
  "enum": "1",
  "floatArray": [ 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0 ],
  "runType": "geometry_converge",
  "ialgo": "method1"
}
```

You could also dump the config with DUMP_CONFIG(), or dump the parameters with DUMP_PARAMETERS() to standard output or to a file/handler
```python
>>> params.DUMP_CONFIG()
{'test_key': {'key': 'test_key', 'type': 'float', 'enumItems': None, 'enumVals': None, 'isArray': True, 'length': 6, 'default': 0.0, 'comments': '', 'reference': ''}}
>>> params.DUMP_PARAMETERS()
{'__keys_config': {'test_key': {'key': 'test_key', 'type': 'float', 'enumItems': None, 'enumVals': None, 'isArray': True, 'length': 6, 'default': 0.0, 'comments': '', 'reference': ''}}, '__keys_values': {'test_key': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}}
>>> params.DUMP_CONFIG('config.json')
>>> params.DUMP_PARAMETERS('parameters.json')
```

Have Fun!

