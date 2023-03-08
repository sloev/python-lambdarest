![test](https://github.com/sloev/python-lambdarest/actions/workflows/test.yml/badge.svg) [![Latest Version](https://img.shields.io/pypi/v/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest) [![Python Support](https://img.shields.io/pypi/pyversions/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest)

# Lambdarest Documentation

Here you find updated documentation on how to use Lambdarest, please check as well the [tests](https://github.com/trustpilot/python-lambdarest/blob/master/docs/tests/) directory for some more examples.

Lambdarest is a product of collaboration, please consider [Contributing](https://github.com/trustpilot/python-lambdarest/blob/master/docs/CONTRIBUTING.md) if you have an [issue](https://github.com/trustpilot/python-lambdarest/issues/new/choose) or a [feature](https://github.com/trustpilot/python-lambdarest/pulls) :-)


**Contents**

* [Installation](#installation)
* [Articles / Turorials](#external-articles--tutorials)
* [Getting started](#getting-started)
* [Advanced usage example](#advanced-usage)
* [Query params](#query-params)
* [Headers and MultiValueHeaders](#headers-and-multivalueheaders)
* [Routing](#routing)
* [Authorization Scopes](#authorization-scopes)
* [Exception Handling](#exception-handling)
* [AWS Application Load Balancer](#aws-application-load-balancer)
* [Base 64 encoded body](#base-64-encoded-body)
* [Tests](#tests)

## Installation

Install the package from [PyPI](http://pypi.python.org/pypi/) using [pip](https://pip.pypa.io/):

```bash
$ pip install lambdarest
```

## External articles / tutorials

* [devgrok.com: Create a Private Microservice Using an Application Load Balancer](http://www.devgrok.com/2019/03/create-private-microservice-using.html)

  Article about how to use **lambdarest** with **AWS Application Load Balancer**

* [rockset.com: Building a Serverless Microservice Using Rockset and AWS Lambda](https://rockset.com/blog/building-a-serverless-microservice-using-rockset-and-aws-lambda/)

  Article about how to set up **lambdarest** in AWS infrastructure

**Other articles? add them [here](https://github.com/trustpilot/python-lambdarest/issues/55)**

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
def validate_example(event):
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

## Query Params

Query parameters are also analyzed and validatable with JSON schemas.

Query arrays are expected to be comma separated.

All values are unpacked to types defined in `schema.properties.query.properties.*`, see the **examples underneath**

The resulting query args are tested against the full jsonschema together with the body, headers etc.

### Float array example

In jsonschema **number** covers both ints and floats, in lambdarest all **number**s are cast as floats.

<details>
  <summary>Expand example</summary>
 
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

    @lambda_handler.handle("get", path="/with-params/floats", schema=my_schema)
    def float_example(event):
        return event["json"]["query"]


    ##### TEST #####


    valid_input_event = {
        "queryStringParameters": {
            "foo": "1, 2.2, 3"
        },
        "httpMethod": "GET",
        "resource": "/with-params/floats"
    }
    result = lambda_handler(event=valid_input_event)
    assert result == {"body": '{"foo": [1.0, 2.2, 3.0]}', "statusCode": 200, "headers":{}}
    ```
</details>


### Integer array example

Specify array type as integer to get int casting

<details>
  <summary>Expand example</summary>
 
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
                            "type": "integer"
                        }
                    }
                }
            }
        }
    }

    @lambda_handler.handle("get", path="/with-params/integers", schema=my_schema)
    def integer_example(event):
        return event["json"]["query"]


    ##### TEST #####


    valid_input_event = {
        "queryStringParameters": {
            "foo": "1, 2.2, 3"
        },
        "httpMethod": "GET",
        "resource": "/with-params/integers"
    }
    result = lambda_handler(event=valid_input_event)
    assert result == {"body": '{"foo": [1, 2, 3]}', "statusCode": 200, "headers":{}}
    ```
</details>

### String array example

Specify array type as string to get an array of strings **beware of spaces after commas, they are respected!**

<details>
  <summary>Expand example</summary>
 
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
                            "type": "string"
                        }
                    }
                }
            }
        }
    }

    @lambda_handler.handle("get", path="/with-params/strings", schema=my_schema)
    def string_example(event):
        return event["json"]["query"]


    ##### TEST #####


    valid_input_event = {
        "queryStringParameters": {
            "foo": "1, 2.2, 3"
        },
        "httpMethod": "GET",
        "resource": "/with-params/strings"
    }
    result = lambda_handler(event=valid_input_event)
    assert result == {"body": '{"foo": ["1", " 2.2", " 3"]}', "statusCode": 200, "headers":{}}
    ```
</details>


### Behavior with missing query args specs in jsonschema

If no json schema is supplied for the input schema Lambdarest will try to behave consistently and cast according to this pseudocode:

```
try: 
    return json.loads(raw_value)  # this will cover majority of types
except:
    return raw_value
```

## Headers and MultiValueHeaders

You can return headers as part of your response, there is two types of headers:

* **headers**: a dictionary
* **multiValueHeaders**: a dictionary with multiple values for each key

You can populate the headers in the following ways:

1. return tuple with *normal header*

```python
return {'some':'json'}, 200, {'header':'value'}
```

2. return tuple with *normal header* **and** *multiValueHeaders*

```python
return {'some':'json'}, 200, {'header':'value'}, {'multi_header': ["foo", "bar"]}
```

3. return tuple with *multiValueHeaders*

*(you need to still populate the headers as an empty dict)*

```python
return {'some':'json'}, 200, {}, {'multi_header': ["foo", "bar"]}
```

4. return [`Response`](https://github.com/trustpilot/python-lambdarest/blob/cd50bb4e1da4f720ef94534ccfd4989f398a9d5d/lambdarest/__init__.py#L17) object

```python
from lambdarest import Response
# with headers
Response({'some':'json'}, 200, headers={'header':'value'})

# with multiValueHeaders
Response({'some':'json'}, 200, multiValueHeaders={'multi_header': ["foo", "bar"]})

# with headers and multiValueHeaders
Response({'some':'json'}, 200, headers={'header':'value'}, multiValueHeaders={'multi_header': ["foo", "bar"]})
```

## Routing

You can also specify which path to react on for individual handlers using the `path` param:

```python
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/foo/bar/baz")
def routing_example(event):
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
def path_param_example(event, id):
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
def double_path_param_example(event, object_id, foo):
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
def api_proxy_example(event, path):
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

## Authorization Scopes

If you're using a Lambda authorizer, you can pass authorization scopes as input into your Lambda function.

This is useful when using the API Gateway with a Lambda authorizer and have the Lambda authorizer return in a scopes json object the permissions (scopes) the caller has access to. In your Lambda function you can specify what scopes the caller should have to call that function. If the requested scope was not provided by the Lambda authorizer, a 403 error code is given.

The API gateway has the limitation it can only pass primitive data types from a Lambda authorizer function. The scopes list therefore needs to be json encoded by the authorizer function.

To use this, add a scopes attribute to the handler with the list of scopes your function requires. They will be verified from the requestContext.authorizer.scopes attribute from the Lambda authorizer.

```python
from lambdarest import lambda_handler

@lambda_handler.handle("get", path="/private1", scopes=["myresource.read"])
def private_example(event):
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
def private_example_2(event):
    return {"this": "will be json dumped"}

##### TEST #####

input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "resource": "/private2"
}
result = lambda_handler(event=input_event)
assert result == {"body": "Permission denied", "statusCode": 403, "headers":{}}
```

## Exception Handling

By default, this framework provides a simple error handling function that catches all exceptions thrown by the handlers and converts them into `500 {error message}` responses. You can either specify your own error handler or not provide one at all. In the latter case, the exceptions will be raised outside of `lambdarest.handle` function.

```python
import traceback
from lambdarest import create_lambda_handler

# Option 1: provide your own exception handler
def error_handler(error, method):
    print('Error:', str(error), 'in', method)
   
lambda_handler = create_lambda_handler(error_handler=error_handler)

# Option 2: raise all exceptions and handle them outside lambdarest
lambda_handler = create_lambda_handler(error_handler=None)

try:
    result = lambda_handler(event=event)
except:
    traceback.print_exc()
    result = {'statusCode': 500, 'body': 'Internal Server Error'}
```

## AWS Application Load Balancer

In order to use it with Application Load Balancer you need to create your own lambda_handler and not use the singleton:

```python
from lambdarest import create_lambda_handler

lambda_handler = create_lambda_handler(application_load_balancer=True)

@lambda_handler.handle("get", path="/foo/integer/<int:id>/")
def application_load_balancer_example(event, id):
    return {"my-id": id}


##### TEST #####


input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "resource": "/foo/integer/1234/"
}
result = lambda_handler(event=input_event)
assert result == {"body": '{"my-id": 1234}', "statusCode": 200, "headers":{}, "statusDescription": "HTTP OK", "isBase64Encoded": False}
```

## Base 64 encoded body

You can choose to return base64 encoded body by specifying the `isBase64Encoded` param in the return dict.

```python
import base64
from lambdarest import create_lambda_handler

lambda_handler = create_lambda_handler(application_load_balancer=True)

@lambda_handler.handle("get", path="/base64")
def base64_example(event):
    return {
        'statusCode': 200,
        'body': base64.b64encode("test of base64 encoding for ALB".encode("utf8")).decode("utf-8"),
        'isBase64Encoded': True,
        'headers': {
            'Content-Type': "text/plain"
        }
    }


##### TEST #####


input_event = {
    "body": '{}',
    "httpMethod": "GET",
    "resource": "/base64"
}
result = lambda_handler(event=input_event)
assert result == {
    "body": "dGVzdCBvZiBiYXNlNjQgZW5jb2RpbmcgZm9yIEFMQg==",
    "statusCode": 200,
    'headers': {
        'Content-Type': "text/plain"
    },
    "statusDescription": "HTTP OK",
    "isBase64Encoded": True
}
```

## CORS

You can wrap the lambda_handler in CORS to finegrain access.

```python
from lambdarest import lambda_handler, CORS

CORS(lambda_handler, origin="*", methods=["GET"])

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
assert result == {"body": '{"this": "will be json dumped"}', "statusCode": 200, "headers":{"Access-Control-Allow-Methods":"GET", "Access-Control-Allow-Origin": "*"}}
```

## Tests

Use the following commands to install requirements and run test-suite:

```bash
$ pip install -e ".[dev]"
$ black tests/ lambdarest/
$ rm -f test_readme.py
$ pytest --doctest-modules -vvv
```

For more info see [Contributing...](https://github.com/trustpilot/python-lambdarest/blob/master/docs/CONTRIBUTING.md)
