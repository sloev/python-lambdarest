![test](https://github.com/sloev/python-lambdarest/actions/workflows/test.yml/badge.svg) [![Latest Version](https://img.shields.io/pypi/v/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest) [![Python Support](https://img.shields.io/pypi/pyversions/lambdarest.svg)](https://pypi.python.org/pypi/lambdarest)


# lambdarest

Python routing mini-framework for [AWS Lambda](https://aws.amazon.com/lambda/) with optional JSON-schema validation.

### Features

* `lambda_handler` function constructor with built-in dispatcher
* Decorator to register functions to handle HTTP methods
* Optional JSON-schema input validation using same decorator

### Support the development ❤️

You can support the development by:

1. [Contributing code](https://github.com/trustpilot/python-lambdarest/blob/master/docs/CONTRIBUTING.md)
2. [Buying the maintainer a coffee](https://buymeacoffee.com/sloev)
3. [Buying some Lambdarest swag](https://www.redbubble.com/i/mug/Lambdarest-by-sloev/73793554.9Q0AD)

    like this mug for example: 

    [![lambdarest mug](https://raw.githubusercontent.com/sloev/python-lambdarest/master/.github/lambdarest_mug.png)](https://www.redbubble.com/i/mug/Lambdarest-by-sloev/73793554.9Q0AD)

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

## Documentation

See [docs](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md) for **documentation and examples** covering amongst:

* [Advanced usage example](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md#advanced-usage)
* [Query params](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md#query-params)
* [Headers and MultiValueHeaders](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md#headers-and-multivalueheaders)
* [Routing](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md#routing)
* [Authorization Scopes](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md#authorization-scopes)
* [Exception Handling](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md#exception-handling)
* [AWS Application Load Balancer](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md#aws-application-load-balancer)
* [CORS](https://github.com/trustpilot/python-lambdarest/blob/master/docs/README.md#cors)


## Anormal unittest behaviour with `lambda_handler` singleton

Because of python unittests leaky test-cases it seems like you shall beware of [this issue](https://github.com/trustpilot/python-lambdarest/issues/16) when using the singleton `lambda_handler` in a multiple test-case scenario.

## Tests

Use the following commands to install requirements and run test-suite:

```bash
$ pip install -e ".[dev]"
$ black tests/ lambdarest/
$ rm -f test_readme.py
$ pytest --doctest-modules -vvv
```

For more info see [Contributing...](https://github.com/trustpilot/python-lambdarest/blob/master/docs/CONTRIBUTING.md)

## Changelog

See [HISTORY.md](https://github.com/trustpilot/python-lambdarest/blob/master/docs/HISTORY.md)

## Contributors

Thanks for contributing!

[@sphaugh](https://github.com/sphaugh), [@amacks](https://github.com/amacks), [@jacksgt](https://github.com/jacksgt), [@mkreg](https://github.com/mkreg), [@aphexer](https://github.com/aphexer), [@nabrosimoff](https://github.com/nabrosimoff), [@elviejokike](https://github.com/elviejokike), [@eduardomourar](https://github.com/eduardomourar), [@devgrok](https://github.com/devgrok), [@AlbertoTrindade](https://github.com/AlbertoTrindade), [@paddie](https://github.com/paddie), [@svdgraaf](https://github.com/svdgraaf), [@simongarnier](https://github.com/simongarnier), [@martinbuberl](https://github.com/martinbuberl), [@adamelmore](https://github.com/adamelmore), [@sloev](https://github.com/sloev)

[Wanna contribute?](https://github.com/trustpilot/python-lambdarest/blob/master/docs/CONTRIBUTING.md)

And by the way, we have a [Code Of Friendlyhood!](https://github.com/trustpilot/python-lambdarest/blob/master/docs/CODE_OF_CONDUCT.md)
