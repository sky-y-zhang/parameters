# parameters
Parameters is design for large program with massive parameters. It supports integer, float, string and enumerate types. For integer and float, array is supported as well. Type protection is valid inside. And load/dump of parameters is available. 

```python
params = parameters.Parameters()
params = parameters.Parameters(parameter_json)
```
After the parameter instance is generated, key can be add/updated/removed, val can be set/reset
```python
>>> params.update_key('test_key', 'int', default=0)
>>> params
{"test_key": 0}
>>> params.remove_key('test_key')
>>> params.test_key = 1
>>> params
{"test_key": 1}
>>> params.test_key
1
>>> params.reset_key('test_key')
>>> params
{"test_key": 0}
```

An integer/float array could be initiate with
```python
>>> params.update_key('test_key', 'int', length=10, default=0)
>>> params
{"test_key": "[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"}
>>> params.update_key('test_key', 'float', length=6, default=0)
>>> params
{"test_key": "[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]"}
```

You could get a beautiful output with the instance or use the print function
```python
>>> params
{
  "string": "STRINGSING",
  "int": 1,
  "float": 1.1,
  "enumerate": "1",
  "floatArray": [ 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0 ],
  "intArray": [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
}
```

 You could also dump the config with dump_config(), or dump the parameters with dump_parameters()

Have Fun!
