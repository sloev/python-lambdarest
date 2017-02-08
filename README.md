[![Build Status](http://travis-ci.org/trustpilot/python-lambdarest.svg?branch=master)](https://travis-ci.org/trustpilot/python-lambdarest)  [![pypi](https://badge.fury.io/py/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest)  [![trustpilot](https://images-static.trustpilot.com/api/logos/light-bg/120x14.png)](https://trustpilot.com)

# Lambdarest - python pico framework for AWS lambda

Pico framework for AWS lambda with optional JSON-schema validation.

&nbsp;


###Includes:###
* lambda_handler function constructor with builtin dispatcher
* decorator to register functions to handle http-methods
* optional JSON-schema input validation using same decorator

## install

###Python versions###
Tested on 2.7, 3.3, 3.4, 3.5
see `tox.ini` for more info.

###dependencies###
Requires the following dependencies (will be installed automatically):
```
jsonschema>=2.5.1
strict-rfc3339>=0.7
```

###Install from pypi###
```
pip install lambdarest
```

###Install from git###
```
pip install git+https://github.com/trustpilot/python-lambdarest.git
or
git clone https://github.com/trustpilot/python-lambdarest.git
cd python-lambdarest
sudo python setup.py install
```

## Usage
This module gives you the option of using different functions to handle
different http methods.

```python
from lambdarest import create_lambda_handler

lambda_handler = create_lambda_handler()

@lambda_handler.handle("get")
def my_own_get(event):
    return {"this": "will be json dumped"}

input_event = {
    "body": '{}',
    "httpMethod": "GET"
}
result = lambda_handler(event=input_event)
assert result == {"body": '{"this": "will be json dumped"}', "statusCode": 200, "headers":{}}
```

Optionally you can also validate incomming json body with JSON schemas
```python
from lambdarest import create_lambda_handler

lambda_handler = create_lambda_handler()

my_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "foo": {
            "type": "string"
        }
    }
}

@lambda_handler.handle("get", schema=my_schema)
def my_own_get(event):
    return {"this": "will be json dumped"}

valid_input_event = {
    "body": '{"foo":"bar"}',
    "httpMethod": "GET"
}
result = lambda_handler(event=valid_input_event)
assert result == {"body": '{"this": "will be json dumped"}', "statusCode": 200, "headers":{}}


invalid_input_event = {
    "body": '{"foo":666}',
    "httpMethod": "GET"
}
result = lambda_handler(event=invalid_input_event)
assert result == {"body": '"Validation Error"', "statusCode": 400, "headers":{}}
```

## Tests
* Use pytest to run tests with current python version.
* Use tox or the builtin `test-all` make target to run tests for all platforms

```
$ make test-all
```
dependencies for tests: see requirements_dev.txt


## Contributions

* use github issues for bugs/requests
* PR's welcome, will be code reviewed
