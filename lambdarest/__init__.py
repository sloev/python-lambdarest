# -*- coding: utf-8 -*-
import json
import logging
from string import Template
from jsonschema import validate, ValidationError, FormatChecker
from werkzeug.routing import Map, Rule, NotFound
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException
from distutils.util import strtobool

from functools import wraps, reduce
from typing import TypeVar, Union, List, Callable

__validate_kwargs = {"format_checker": FormatChecker()}
__required_keys = ["httpMethod"]
__either_keys = ["path", "resource"]


class Response(object):
    """Class to conceptualize a response with default attributes

    if no body is specified, empty string is returned
    if no status_code is specified, 200 is returned
    if no headers are specified, empty dict is returned
    """

    def __init__(
        self,
        body=None,
        status_code=None,
        headers=None,
        multiValueHeaders=None,
        isBase64Encoded=False,
    ):
        self.body = body
        self.status_code = status_code
        self.headers = headers
        self.multiValueHeaders = multiValueHeaders
        self.status_code_description = None
        self.isBase64Encoded = isBase64Encoded

    def to_json(self, encoder=json.JSONEncoder, application_load_balancer=False):
        """Generates and returns an object with the expected field names.

        Note: method name is slightly misleading, should be populate_response or with_defaults etc
        """
        status_code = self.status_code or 200
        # if it's already a str, we don't need json.dumps
        do_json_dumps = self.body is not None and not isinstance(self.body, str)
        response = {
            "body": json.dumps(self.body, cls=encoder, sort_keys=True)
            if do_json_dumps
            else self.body,
            "statusCode": status_code,
        }
        # handle multiValueHeaders if defined, default to headers
        if self.multiValueHeaders == None:
            response["headers"] = self.headers or {}
        else:
            response["multiValueHeaders"] = self.multiValueHeaders
        # if body is None, remove the key
        if response.get("body") == None:
            response.pop("body")

        if application_load_balancer:
            response.update(
                {
                    # note must be HTTP [description] as per:
                    #   https://docs.aws.amazon.com/lambda/latest/dg/services-alb.html
                    # the value of 200 OK fails:
                    #   https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html#respond-to-load-balancer
                    "statusDescription": self.status_code_description
                    or "HTTP " + HTTP_STATUS_CODES[status_code],
                    "isBase64Encoded": self.isBase64Encoded,
                }
            )
        return response


# Response headers
ACL_ORIGIN = "Access-Control-Allow-Origin"
ACL_METHODS = "Access-Control-Allow-Methods"
ACL_CREDENTIALS = "Access-Control-Allow-Credentials"
ACL_MAX_AGE = "Access-Control-Max-Age"

ALL_METHODS = ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"]


def CORS(
    lambda_handler,
    origin="*",
    methods=ALL_METHODS,
    supports_credentials=False,
    max_age=None,
):
    def cors_after_request(response: Response) -> Response:
        headers = response.headers
        if headers is None:
            headers = dict()

        headers.update({ACL_ORIGIN: origin, ACL_METHODS: ", ".join(methods)})
        if supports_credentials:
            headers.update({ACL_CREDENTIALS: supports_credentials})
        if max_age:
            headers.update({ACL_MAX_AGE: max_age})

        response.headers = headers
        return response

    lambda_handler.after_request(cors_after_request)
    return lambda_handler


T = TypeVar("T")
Maybe = Union[None, T]


# If it returns a Response, the value is handled as if it was the return
# value from the view, and further request handling is stopped.
BeforeRequestCallable = Callable[[], Maybe[Response]]


# The function is called with the response object, and must return a response
# object. This allows the functions to modify or replace the response before it
# is sent.
AfterRequestCallable = Callable[[Response], Response]


class ScopeMissing(Exception):
    pass


def __cast_list(value, type):
    values_list = value.split(",")

    def inner_cast(inner_type):
        try:
            return list(map(inner_type, values_list))
        except TypeError:
            pass
        except ValueError:
            pass
        return None

    return inner_cast(type) or inner_cast(str) or value


def __cast_bool(bool_string):
    try:
        bool(strtobool(bool_string))
    except TypeError:
        pass
    return bool_string


def __marshall_value(value, query_param_schema_fragment):
    value_type = query_param_schema_fragment.get("type", None)

    try:
        if value_type == "array":
            array_type = query_param_schema_fragment.get("items", {}).get("type", None)

            if array_type == "string":
                return __cast_list(value, str)
            elif array_type == "integer":
                return __cast_list(value, lambda x: int(float(x)))
            elif array_type == "number":
                return __cast_list(value, float)
            elif array_type == "boolean":
                return __cast_list(value, __cast_bool)
        elif value_type == "string":
            return value
        elif value_type == "integer":
            return int(value)
        elif value_type == "number":
            return float(value)
        elif value_type == "boolean":
            return __cast_bool(value)
    except TypeError:
        pass

    return value


def __json_load_query(query, query_param_schema=None):
    query = query or {}
    query_param_schema = query_param_schema or {}

    return {
        key: __marshall_value(value, query_param_schema.get(key, {}))
        for key, value in query.items()
    }


def default_error_handler(error, method):
    logging_message = "[%s][{status_code}]: {message}" % method
    logging.exception(logging_message.format(status_code=500, message=str(error)))


def check_update_and_fill_resource_placeholders(resource, path_parameters):
    """
    Prepare resource parameters before routing.
    In case when resource defined as /path/to/{placeholder}/resource,
    the router can't find a correct handler.
    This method inserts path parameters
    instead of placeholders and returns the result.

    :param resource: Resource path definition
    :param path_parameters: Path parameters dict
    :return: resource definition with inserted path parameters
    """
    base_resource = resource

    # prepare resource.
    # evaluate from /foo/{key1}/bar/{key2}/{proxy+}
    # to /foo/${key1}/bar/${key2}/{proxy+}

    if path_parameters is not None:
        for path_key in path_parameters:
            resource = resource.replace("{%s}" % path_key, "${%s}" % path_key)
    else:
        return base_resource

    # insert path_parameteres by template
    # /foo/${key1}/bar/${key2}/{proxy+} -> /foo/value1/bar/value2/{proxy+}
    template = Template(resource)
    try:
        resource = template.substitute(**(path_parameters))
        return resource
    except KeyError:
        return base_resource


def __pipe_funcs(*funcs: Callable[[T], T]):
    def pipe(value):
        return reduce(lambda r, f: f(r), funcs, value)

    return pipe


def create_lambda_handler(
    error_handler=default_error_handler,
    json_encoder=json.JSONEncoder,
    application_load_balancer=False,
):
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
    before_request_handlers: List[BeforeRequestCallable] = []
    after_request_handlers: List[AfterRequestCallable] = []

    def inner_lambda_handler(event, context=None):
        apply_after_request_handlers = __pipe_funcs(*after_request_handlers)

        # check if running as "aws lambda proxy"
        if (
            not isinstance(event, dict)
            or not all(key in event for key in __required_keys)
            or not any(key in event for key in __either_keys)
        ):
            message = "Bad request, maybe not using Lambda Proxy?"
            logging.error(message)
            return Response(message, 500).to_json(
                application_load_balancer=application_load_balancer
            )

        # Save context within event for easy access
        event["context"] = context
        # for application load balancers, no api definition is used hence no resource is set so just use path
        if "resource" not in event:
            resource = event["path"]
        else:
            resource = event["resource"]

        # Fill placeholders in resource path
        if "pathParameters" in event:
            resource = check_update_and_fill_resource_placeholders(
                resource, event["pathParameters"]
            )

        path = resource

        # Check if a path is set, if so, check if the base path is the same as
        # the resource. If not, this is an api with a custom domainname.
        # if so, the path will contain the actual request, but it will be
        # prefixed with the basepath, which needs to be removed. Api Gateway
        # only supports single level basepaths
        # eg:
        # path: /v2/foo/foobar
        # resource: /foo/{name}
        # the /v2 needs to be removed
        if "path" in event and event["path"].split("/")[1] != resource.split("/")[1]:
            path = "/%s" % "/".join(event["path"].split("/")[2:])

        # proxy is a bit weird. We just replace the value in the uri with the
        # actual value provided by apigw, and use that
        if "{proxy+}" in resource:
            path = resource.replace("{proxy+}", event["pathParameters"]["proxy"])

        method_name = event["httpMethod"].lower()
        func = None
        kwargs = {}
        error_tuple = ("Internal server error", 500)
        logging_message = "[%s][{status_code}]: {message}" % method_name
        try:
            # bind the mapping to an empty server name
            mapping = url_maps.bind("")
            rule, kwargs = mapping.match(path, method=method_name, return_rule=True)
            func = rule.endpoint

            # if this is a catch-all rule, don't send any kwargs
            if rule.rule == "/<path:path>":
                kwargs = {}
        except NotFound as e:
            logging.warning(logging_message.format(status_code=404, message=str(e)))
            error_tuple = (str(e), 404)

        if func:
            try:
                for handler in before_request_handlers:
                    # pylint: disable=E1128
                    response = handler()
                    if response:
                        return response.to_json(
                            application_load_balancer=application_load_balancer
                        )

                response = func(event, **kwargs)
                if not isinstance(response, Response):
                    # Set defaults
                    status_code = headers = multiValueHeaders = None
                    isBase64Encoded = False

                    if isinstance(response, tuple):
                        response_len = len(response)
                        if response_len > 3:
                            raise ValueError("Response tuple has more than 3 items")

                        # Unpack the tuple, missing items will be defaulted
                        body, status_code, headers, multiValueHeaders = response + (
                            None,
                        ) * (4 - response_len)

                    elif isinstance(response, dict) and all(
                        key
                        in [
                            "body",
                            "statusCode",
                            "headers",
                            "multiValueHeaders",
                            "statusDescription",
                            "isBase64Encoded",
                        ]
                        for key in response.keys()
                    ):
                        body = response.get("body")
                        status_code = response.get("statusCode") or status_code
                        headers = response.get("headers") or headers
                        multiValueHeaders = (
                            response.get("multiValueHeaders") or multiValueHeaders
                        )
                        isBase64Encoded = (
                            response.get("isBase64Encoded") or isBase64Encoded
                        )

                    else:  # if response is string, int, etc.
                        body = response
                    response = Response(
                        body, status_code, headers, multiValueHeaders, isBase64Encoded
                    )

                response = apply_after_request_handlers(response)

                return response.to_json(
                    encoder=json_encoder,
                    application_load_balancer=application_load_balancer,
                )

            except ValidationError as error:
                error_description = "Schema[{}] with value {}".format(
                    "][".join(str(error.absolute_schema_path)), error.message
                )
                logging.warning(
                    logging_message.format(status_code=400, message=error_description)
                )
                error_tuple = ("Validation Error", 400)

            except ScopeMissing as error:
                error_description = "Permission denied"
                logging.warning(
                    logging_message.format(status_code=403, message=error_description)
                )
                error_tuple = (error_description, 403)

            except HTTPException as error:
                logging.warning(
                    logging_message.format(status_code=error.code, message=error.name)
                )
                error_tuple = (error.description, error.code)

            except Exception as error:
                if error_handler:
                    error_handler(error, method_name)
                else:
                    raise

        body, status_code = error_tuple
        response = apply_after_request_handlers(Response(body, status_code))

        return response.to_json(application_load_balancer=application_load_balancer)

    def inner_handler(method_name, path="/", schema=None, load_json=True, scopes=None):
        if schema and not load_json:
            raise ValueError("if schema is supplied, load_json needs to be true")

        query_param_schema = None
        if isinstance(schema, dict):
            query_param_schema = (
                schema.get("properties", {}).get("query", {}).get("properties", {})
            )

        def wrapper(func):
            @wraps(func)
            def inner(event, *args, **kwargs):
                if load_json:
                    try:
                        json_body = json.loads(event.get("body") or "{}")
                    except json.decoder.JSONDecodeError:
                        return Response("Invalid json body", 400)
                    json_data = {
                        "body": json_body,
                        "query": __json_load_query(
                            event.get("queryStringParameters"),
                            query_param_schema=query_param_schema,
                        ),
                    }
                    event["json"] = json_data
                    if schema:
                        # jsonschema.validate using given schema
                        validate(json_data, schema, **__validate_kwargs)

                try:
                    provided_scopes = json.loads(
                        event["requestContext"]["authorizer"]["scopes"]
                    )
                except KeyError:
                    provided_scopes = []
                except json.decoder.JSONDecodeError:
                    # Ignore passed scopes if it isn't properly json encoded
                    provided_scopes = []

                for scope in scopes or []:
                    if scope not in provided_scopes:
                        raise ScopeMissing("Scope: '{}' is missing".format(scope))

                return func(event, *args, **kwargs)

            # if this is a catch all url, make sure that it's setup correctly
            if path == "*":
                target_path = "/*"
            else:
                target_path = path

            # replace the * with the werkzeug catch all path
            if "*" in target_path:
                target_path = target_path.replace("*", "<path:path>")

            # make sure the path starts with /
            if not target_path.startswith("/"):
                raise ValueError("Please configure path with starting slash")

            # register http handler function
            rule = Rule(target_path, endpoint=inner, methods=[method_name.lower()])
            url_maps.add(rule)
            return inner

        return wrapper

    def after_request_handler(func):
        @wraps(func)
        def wrapper(request):
            return func(request)

        after_request_handlers.append(func)

        return wrapper

    def before_request_handler(func):
        @wraps(func)
        def wrapper(request):
            return func(request)

        before_request_handlers.append(func)

        return wrapper

    lambda_handler = inner_lambda_handler
    lambda_handler.handle = inner_handler
    lambda_handler.before_request = before_request_handler
    lambda_handler.after_request = after_request_handler
    return lambda_handler


# singleton
lambda_handler = create_lambda_handler()
