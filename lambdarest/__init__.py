# -*- coding: utf-8 -*-
"""Lambdarest - python pico framework for AWS lambda

copyright Trustpilot 2017
License: MIT
"""

__author__ = """sloev"""
__email__ = 'jgv@trustpilot.com'
__version__ = '0.0.2'


import json
import logging
from jsonschema import validate, ValidationError, FormatChecker


validate_kwargs = {"format_checker": FormatChecker()}


class Response:
    """Class to conceptualize a response with defaulted attributes

    if no body is specified, empty string is returned
    if no status_code is specified, 200 is returned
    if no headers ae specified, empty dict is returned
    """

    def __init__(self, body=None, status_code=None, headers=None):
        self.body = body
        self.status_code = status_code
        self.headers = headers

    def to_json(self):
        return {
            "body": json.dumps(self.body or ""),
            "statusCode": self.status_code or 200,
            "headers": self.headers or {}
        }


def create_lambda_handler():
    """Create a lambda handler function with `handle` decorator as attribute

    example:
        lambda_handler = create_lambda_handler()
        lambda_handler.handle("get")
        def my_get_func(event):
            pass

    Inner_lambda_handler:
    is the one you will receive when calling this
    function. It acts like a dispatcher calling the registered http handler
    functions on the basis of the incomming httpMethod.
    All responses are formatted using the lambdarest.Response class.

    Inner_handler:
    Is the decorator function used to register funtions as handlers of
    different http methods.
    The inner_handler is also able to validate incomming data using a specified
    JSON schema, please see http://json-schema.org for info.

    """
    http_methods = {}

    def inner_lambda_handler(event, context=None):
        # Save context within event for easy access
        event["context"] = context
        method_name = event["httpMethod"].lower()
        func = None
        error_tuple = ("[Error", 500)
        logging_message = "[%s][{status_code}]: {message}" % method_name
        try:
            func = http_methods[method_name]

        except KeyError:
            logging.warning(logging_message.format(
                status_code=405, message="Not supported"))
            error_tuple = ("Not supported", 405)

        if func:
            try:
                response = func(event)
                if not isinstance(response, Response):
                    # Set defaults
                    status_code = headers = None

                    if isinstance(response, tuple):
                        response_len = len(response)
                        if response_len > 3:
                            raise ValueError(
                                "Response tuple has more than 3 items")

                        # Unpack the tuple, missing items will be defaulted to None
                        body, status_code, headers = response + (None,) * (
                            3 - response_len)

                    else:  # if response is string, dict, etc,
                        body = response
                    response = Response(body, status_code, headers)
                return response.to_json()

            except ValidationError as error:
                error_description = "Schema[{}] with value {}".format(
                    "][".join(error.absolute_schema_path), error.message)
                logging.warning(logging_message.format(
                    status_code=400, message=error_description))
                error_tuple = ("Validation Error", 400)

            except Exception as error:
                # no runtime exceptions are left unhandled
                logging.exception(logging_message.format(
                    status_code=500, message=str(error)))

        body, status_code = error_tuple
        return Response(body, status_code).to_json()

    def inner_handler(method_name, schema=None, load_json=True):
        if schema and not load_json:
            raise ValueError(
                "if schema is supplied, load_json needs to be true")

        def wrapper(func):
            def inner(event, *args, **kwargs):
                if load_json:
                    json_data = json.loads(event["body"])
                    event["json"] = json_data
                    if schema:
                        # jsonschema.validate using given schema
                        validate(json_data, schema, **validate_kwargs)
                return func(event, *args, **kwargs)

            # register http handler function
            http_methods[method_name] = inner
            return inner
        return wrapper

    lambda_handler = inner_lambda_handler
    lambda_handler.handle = inner_handler
    return lambda_handler
