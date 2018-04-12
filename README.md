# lambdarest

[![Build Status](http://travis-ci.org/trustpilot/python-lambdarest.svg?branch=master)](https://travis-ci.org/trustpilot/python-lambdarest)  [![Latest Version](https://img.shields.io/pypi/v/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest) [![Python Support](https://img.shields.io/pypi/pyversions/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest)

Python routing mini-framework for [AWS Lambda](https://aws.amazon.com/lambda/) with optional JSON-schema validation.

### Features

* `lambda_handler` function constructor with built-in dispatcher
* Decorator to register functions to handle HTTP methods
* Optional JSON-schema input validation using same decorator

## Installation

Install the package from [PyPI](http://pypi.python.org/pypi/) using [pip](https://pip.pypa.io/):

```bash
pip install lambdarest
```

## Getting Started

This module helps you to handle different HTTP methods in your AWS Lambda.

```python
from lambdarest import lambda_handler

@lambda_handler.handle("get")
def my_own_get(event):
    return {"this": "will be json dumped"}


##### TEST #####


input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "resource": "/"
}
result = lambda_handler(event=input_event)
assert result == {"body": '{"this": "will be json dumped"}', "statusCode": 200, "headers":{}}
```

## Advanced Usage

Optionally you can validate an incoming JSON body against a JSON schema:

```python
from lambdarest import lambda_handler

my_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "body":{
            "type": "object",
            "properties": {
                "foo": {
                    "type": "string"
                }
            }
        }
    }
}

@lambda_handler.handle("get", path="/with-schema/", schema=my_schema)
def my_own_get(event):
    return {"this": "will be json dumped"}


##### TEST #####


valid_input_event = {
    "body": '{"foo":"bar"}',
    "httpMethod": "GET",
    "resource": "/with-schema/"
}
result = lambda_handler(event=valid_input_event)
assert result == {"body": '{"this": "will be json dumped"}', "statusCode": 200, "headers":{}}


invalid_input_event = {
    "body": '{"foo":666}',
    "httpMethod": "GET",
    "resource": "/with-schema/"
}
result = lambda_handler(event=invalid_input_event)
assert result == {"body": '"Validation Error"', "statusCode": 400, "headers":{}}
```

### Query Params

Query params are also analyzed and validatable with JSON schemas.
Query arrays are expected to be comma separated, all numbers are converted to floats.

```python
from lambdarest import lambda_handler

my_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "query":{
            "type": "object",
            "properties": {
                "foo": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                }
            }
        }
    }
}

@lambda_handler.handle("get", path="/with-params/", schema=my_schema)
def my_own_get(event):
    return event["json"]["query"]


##### TEST #####


valid_input_event = {
    "queryStringParameters": {
        "foo": "1, 2.2, 3"
    },
    "httpMethod": "GET",
    "resource": "/with-params/"
}
result = lambda_handler(event=valid_input_event)
assert result == {"body": '{"foo": [1.0, 2.2, 3.0]}', "statusCode": 200, "headers":{}}
```

### Routing

You can also specify which path to react on for individual handlers using the `path` param:

```python
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/foo/bar/baz")
def my_own_get(event):
    return {"this": "will be json dumped"}


##### TEST #####


input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "resource": "/foo/bar/baz"
}
result = lambda_handler(event=input_event)
assert result == {"body": '{"this": "will be json dumped"}', "statusCode": 200, "headers":{}}
```

And you can specify path parameters as well, which will be passed as keyword arguments:

```python
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/foo/<int:id>/")
def my_own_get(event, id):
    return {"my-id": id}


##### TEST #####


input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "resource": "/foo/1234/"
}
result = lambda_handler(event=input_event)
assert result == {"body": '{"my-id": 1234}', "statusCode": 200, "headers":{}}
```

Or use the Proxy APIGateway magic endpoint:
```python
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/bar/<path:path>")
def my_own_get(event, path):
    return {"path": path}


##### TEST #####

input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "path": "/foo/bar/baz",
    "resource": "/bar/{proxy+}",
    "pathParameters": {
      "proxy": "bar/baz"
    }
}
result = lambda_handler(event=input_event)
assert result == {"body": '{"path": "bar/baz"}', "statusCode": 200, "headers":{}}
```


## Anormal unittest behaviour with `lambda_handler` singleton

Because of python unittests leaky test-cases it seems like you shall beware of [this issue](https://github.com/trustpilot/python-lambdarest/issues/16) when using the singleton `lambda_handler` in a multiple test-case scenario.

## Tests

You can use pytest to run tests against your current Python version. To run tests for all platforms, use tox or the built-in `test-all` Make target:

```
make test-all
```

See [`setup.py`](setup.py) for test dependencies.
