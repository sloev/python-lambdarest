[![Build Status](http://travis-ci.org/trustpilot/python-lambdarest.svg?branch=master)](https://travis-ci.org/trustpilot/python-lambdarest)  [![pypi](https://badge.fury.io/py/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest)

# lambdarest

Python pico framework for [AWS Lambda](https://aws.amazon.com/lambda/) with optional JSON-schema validation.

###Includes###

* `lambda_handler` function constructor with built-in dispatcher
* Decorator to register functions to handle HTTP methods
* Optional JSON-schema input validation using same decorator

## Install

###Python versions###

Tested on 2.7, 3.3, 3.4, 3.5. See [`tox.ini`](tox.ini) for more info.

###Dependencies###

Requires the following dependencies (will be installed automatically):

```
jsonschema>=2.5.1
strict-rfc3339>=0.7
```

###Install from pypi###

```bash
pip install lambdarest
```

###Install from git###

```bash
pip install git+https://github.com/trustpilot/python-lambdarest.git
```

or

```bash
git clone https://github.com/trustpilot/python-lambdarest.git
cd python-lambdarest
sudo python setup.py install
```

## Usage

This module gives you the option of using different functions to handle different HTTP methods.

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

Optionally you can also validate incoming JSON body with JSON schemas:

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

You can use pytest to run tests against your current Python version. To run tests for all platforms, use tox or the built-in `test-all` Make target:

```
$ make test-all
```

See [`requirements_dev.txt`](requirements_dev.txt) for test dependencies.
