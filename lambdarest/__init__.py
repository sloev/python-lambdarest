# -*- coding: utf-8 -*-
import json
import logging
from jsonschema import validate, ValidationError, FormatChecker
from werkzeug.routing import Map, Rule, NotFound


__validate_kwargs = {"format_checker": FormatChecker()}
__required_keys = ["httpMethod", "resource"]


class Response(object):
    """Class to conceptualize a response with default attributes

    if no body is specified, empty string is returned
    if no status_code is specified, 200 is returned
    if no headers are specified, empty dict is returned
    """

    def __init__(self, body=None, status_code=None, headers=None):
        self.body = body
        self.status_code = status_code
        self.headers = headers

    def to_json(self):
        return {
            "body": json.dumps(self.body) if self.body is not None else None,
            "statusCode": self.status_code or 200,
            "headers": self.headers or {}
        }


def _float_cast(value):
    try:
        return float(value)
    except Exception:
        pass
    return value


def _marshall_query_params(value):
    try:
        value = json.loads(value)
    except Exception:
        value_cand = value.split(",")
        if len(value_cand) > 1:
            value = list(map(_float_cast, value_cand))
    return value


def _json_load_query(query):
    query = query or {}

    return {key: _marshall_query_params(value)
            for key, value in query.items()}


def default_error_handler(error, method):
    logging_message = "[%s][{status_code}]: {message}" % method
    logging.exception(logging_message.format(
        status_code=500,
        message=str(error)
    ))


def create_lambda_handler(error_handler=default_error_handler):
    """Create a lambda handler function with `handle` decorator as attribute

    example:
        lambda_handler = create_lambda_handler()
        lambda_handler.handle("get")
        def my_get_func(event):
            pass

    Inner_lambda_handler:
    is the one you will receive when calling this function. It acts like a
    dispatcher calling the registered http handler functions on the basis of the
    incoming httpMethod.
    All responses are formatted using the lambdarest.Response class.

    Inner_handler:
    Is the decorator function used to register funtions as handlers of
    different http methods.
    The inner_handler is also able to validate incoming data using a specified
    JSON schema, please see http://json-schema.org for info.

    """
    url_maps = Map()

    def inner_lambda_handler(event, context=None):
        # check if running as "aws lambda proxy"
        if not isinstance(event, dict) or not all(
                        key in event for key in __required_keys):
            message = "Bad request, maybe not using Lambda Proxy?"
            logging.error(message)
            return Response(message, 500).to_json()

        # Save context within event for easy access
        event["context"] = context
        path = event['resource']

        # Check if a path is set, if so, check if the base path is the same as
        # the resource. If not, this is an api with a custom domainname.
        # if so, the path will contain the actual request, but it will be
        # prefixed with the basepath, which needs to be removed. Api Gateway
        # only supports single level basepaths
        # eg:
        # path: /v2/foo/foobar
        # resource: /foo/{name}
        # the /v2 needs to be removed
        if 'path' in event and event['path'].split('/')[1] != event['resource'].split('/')[1]:
            path = '/%s' % '/'.join(event['path'].split('/')[2:])

        # proxy is a bit weird. We just replace the value in the uri with the
        # actual value provided by apigw, and use that
        if '{proxy+}' in event['resource']:
            path = event['resource'].replace('{proxy+}', event['pathParameters']['proxy'])

        method_name = event["httpMethod"].lower()
        func = None
        kwargs = {}
        error_tuple = ("Internal server error", 500)
        logging_message = "[%s][{status_code}]: {message}" % method_name
        try:
            # bind the mapping to an empty server name
            mapping = url_maps.bind('')
            rule, kwargs = mapping.match(path, method=method_name, return_rule=True)
            func = rule.endpoint

            # if this is a catch-all rule, don't send any kwargs
            if rule.rule == "/<path:path>":
                kwargs = {}
        except NotFound as e:
            logging.warning(logging_message.format(
                status_code=404, message=str(e)))
            error_tuple = (str(e), 404)

        if func:
            try:
                response = func(event, **kwargs)
                if not isinstance(response, Response):
                    # Set defaults
                    status_code = headers = None

                    if isinstance(response, tuple):
                        response_len = len(response)
                        if response_len > 3:
                            raise ValueError(
                                "Response tuple has more than 3 items")

                        # Unpack the tuple, missing items will be defaulted
                        body, status_code, headers = response + (None,) * (
                            3 - response_len)

                    else:  # if response is string, dict, etc.
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
                if error_handler:
                    error_handler(error, method_name)
                else:
                    raise

        body, status_code = error_tuple
        return Response(body, status_code).to_json()

    def inner_handler(method_name, path="/", schema=None, load_json=True):
        if schema and not load_json:
            raise ValueError(
                "if schema is supplied, load_json needs to be true")

        def wrapper(func):
            def inner(event, *args, **kwargs):
                if load_json:
                    json_data = {
                        "body": json.loads(event.get("body") or "{}"),
                        "query": _json_load_query(
                            event.get("queryStringParameters")
                        )
                    }
                    event["json"] = json_data
                    if schema:
                        # jsonschema.validate using given schema
                        validate(json_data, schema, **__validate_kwargs)
                return func(event, *args, **kwargs)

            # if this is a catch all url, make sure that it's setup correctly
            if path == '*':
                target_path = "/*"
            else:
                target_path = path

            # replace the * with the werkzeug catch all path
            if '*' in target_path:
                target_path = target_path.replace('*', '<path:path>')

            # make sure the path starts with /
            if not target_path.startswith('/'):
                raise ValueError("Please configure path with starting slash")

            # register http handler function
            rule = Rule(target_path, endpoint=inner, methods=[method_name.lower()])
            url_maps.add(rule)
            return inner
        return wrapper

    lambda_handler = inner_lambda_handler
    lambda_handler.handle = inner_handler
    return lambda_handler


# singleton
lambda_handler = create_lambda_handler()
