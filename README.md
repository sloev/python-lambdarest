# lambdarest

[![Build Status](https://travis-ci.org/trustpilot/python-lambdarest.svg?branch=master)](https://travis-ci.org/trustpilot/python-lambdarest) [![Latest Version](https://img.shields.io/pypi/v/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest) [![Python Support](https://img.shields.io/pypi/pyversions/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest) [![Examples tested with pytest-readme](http://img.shields.io/badge/readme-tested-brightgreen.svg)](https://github.com/boxed/pytest-readme)


Python routing mini-framework for [AWS Lambda](https://aws.amazon.com/lambda/) with optional JSON-schema validation.

### Features

* `lambda_handler` function constructor with built-in dispatcher
* Decorator to register functions to handle HTTP methods
* Optional JSON-schema input validation using same decorator

### External articles / tutorials

* [devgrok.com: Create a Private Microservice Using an Application Load Balancer](http://www.devgrok.com/2019/03/create-private-microservice-using.html)

  Article about how to use **lambdarest** with **AWS Application Load Balancer**

* [rockset.com: Building a Serverless Microservice Using Rockset and AWS Lambda](https://rockset.com/blog/building-a-serverless-microservice-using-rockset-and-aws-lambda/)

  Article about how to set up **lambdarest** in AWS infrastructure

**Other articles? add them [here](https://github.com/trustpilot/python-lambdarest/issues/55)**

## Installation

Install the package from [PyPI](http://pypi.python.org/pypi/) using [pip](https://pip.pypa.io/):

```bash
$ pip install lambdarest
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
assert result == {"body": 'Validation Error', "statusCode": 400, "headers":{}}
```

### Query Params

Query parameters are also analyzed and validatable with JSON schemas.
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

Or you can specify more complex parametrized resource path and get parameteres as arguments:
```python
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/object/<int:object_id>/props/<string:foo>/get")
def my_own_get(event, object_id, foo):
    return [{"object_id": int(object_id)}, {"foo": foo}]


##### TEST #####

input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "path": "/v1/object/777/props/bar/get",
    "resource": "/object/{object_id}/props/{foo}/get",
    "pathParameters": {
      "object_id": "777",
      "foo":"bar"
    }
}
result = lambda_handler(event=input_event)
assert result == {"body": '[{"object_id": 777}, {"foo": "bar"}]', "statusCode": 200, "headers":{}}

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
    "path": "/v1/bar/baz",
    "resource": "/bar/{proxy+}",
    "pathParameters": {
      "proxy": "bar/baz"
    }
}
result = lambda_handler(event=input_event)
assert result == {"body": '{"path": "bar/baz"}', "statusCode": 200, "headers":{}}
```

### Scopes

If you're using a Lambda authorizer, you can pass authorization scopes as input into your Lambda function.

This is useful when using the API Gateway with a Lambda authorizer and have the Lambda authorizer return in a scopes json object the permissions (scopes) the caller has access to. In your Lambda function you can specify what scopes the caller should have to call that function. If the requested scope was not provided by the Lambda authorizer, a 403 error code is given.

The API gateway has the limitation it can only pass primitive data types from a Lambda authorizer function. The scopes list therefore needs to be json encoded by the authorizer function.

To use this, add a scopes attribute to the handler with the list of scopes your function requires. They will be verified from the requestContext.authorizer.scopes attribute from the Lambda authorizer.

```python
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/private1", scopes=["myresource.read"])
def my_own_get(event):
    return {"this": "will be json dumped"}

##### TEST #####

input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "resource": "/private1",
    "requestContext": {
        "authorizer": {
            "scopes": '["myresource.read"]'
        }
    }
}
result = lambda_handler(event=input_event)
assert result == {"body": '{"this": "will be json dumped"}', "statusCode": 200, "headers":{}}
```
When no scopes are provided by the authorizer but are still requested by your function, a permission denied error is returned.
```python
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/private2", scopes=["myresource.read"])
def my_own_get(event):
    return {"this": "will be json dumped"}

##### TEST #####

input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "resource": "/private2"
}
result = lambda_handler(event=input_event)
print(result)
assert result == {"body": "Permission denied", "statusCode": 403, "headers":{}}
```

## Use it with AWS Application Load Balancer

In order to use it with Application Load Balancer you need to create your own lambda_handler and not use the singleton:

```python
from lambdarest import create_lambda_handler

lambda_handler = create_lambda_handler(application_load_balancer=True)

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
assert result == {"body": '{"my-id": 1234}', "statusCode": 200, "headers":{}, "statusDescription": "HTTP OK", "isBase64Encoded": False}
```

## Anormal unittest behaviour with `lambda_handler` singleton

Because of python unittests leaky test-cases it seems like you shall beware of [this issue](https://github.com/trustpilot/python-lambdarest/issues/16) when using the singleton `lambda_handler` in a multiple test-case scenario.

## Tests

This package uses [Poetry](https://python-poetry.org/docs/) to install requirements and run tests.

Use the following commands to install requirements and run test-suite:

```bash
$ poetry install
$ poetry run task test
```

For more info see [Contributing...](./CONTRIBUTING.md)

## Changelog

See [HISTORY.md](https://github.com/trustpilot/python-lambdarest/blob/master/HISTORY.md)

## Contributors

@aphexer @nabrosimoff, @elviejokike, @eduardomourar, @devgrok, @AlbertoTrindade, @paddie, @svdgraaf, @simongarnier, @martinbuberl, @adamelmore, @sloev

[Wanna contribute?](./CONTRIBUTING.md)

And by the way, we have a [Code Of Friendlyhood!](./CODE_OF_CONDUCT.md)
