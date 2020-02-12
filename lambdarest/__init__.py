# -*- coding: utf-8 -*-
import json
import logging
import sys
from string import Template
from jsonschema import validate, ValidationError, FormatChecker
from werkzeug.routing import Map, Rule, NotFound
from werkzeug.http import HTTP_STATUS_CODES


from functools import wraps

__validate_kwargs = {"format_checker": FormatChecker()}
__required_keys = ["httpMethod"]
__either_keys = ["path", "resource"]


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
        self.status_code_description = None
        self.isBase64_encoded = False

    def to_json(self, encoder=json.JSONEncoder, application_load_balancer=False):
        """Generates and returns an object with the expected field names.

        Note: method name is slightly misleading, should be populate_response or with_defaults etc
        """
        status_code = self.status_code or 200
        # if it's already a str, we don't need json.dumps
        do_json_dumps = self.body and not isinstance(self.body, str)
        response = {
            "body": json.dumps(self.body, cls=encoder) if do_json_dumps else self.body,
            "statusCode": status_code,
            "headers": self.headers or {},
        }
        if application_load_balancer:
            response.update(
                {
                    # note must be HTTP [description] as per:
                    #   https://docs.aws.amazon.com/lambda/latest/dg/services-alb.html
                    # the value of 200 OK fails:
                    #   https://docs.aws.amazon.com/elasticloadbalancing/latest/application/lambda-functions.html#respond-to-load-balancer
                    "statusDescription": self.status_code_description
                    or "HTTP " + HTTP_STATUS_CODES[status_code],
                    "isBase64Encoded": self.isBase64_encoded,
                }
            )
        return response


def __float_cast(value):
    try:
        return float(value)
    except Exception:
        pass
    return value


def __marshall_query_params(value):
    try:
        value = json.loads(value)
    except Exception:
        value_cand = value.split(",")
        if len(value_cand) > 1:
            value = list(map(__float_cast, value_cand))
    return value


def __json_load_query(query):
    query = query or {}

    return {key: __marshall_query_params(value) for key, value in query.items()}


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

    def inner_lambda_handler(event, context=None):
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
                response = func(event, **kwargs)
                if not isinstance(response, Response):
                    # Set defaults
                    status_code = headers = None

                    if isinstance(response, tuple):
                        response_len = len(response)
                        if response_len > 3:
                            raise ValueError("Response tuple has more than 3 items")

                        # Unpack the tuple, missing items will be defaulted
                        body, status_code, headers = response + (None,) * (
                            3 - response_len
                        )

                    else:  # if response is string, dict, etc.
                        body = response
                    response = Response(body, status_code, headers)
                return response.to_json(
                    encoder=json_encoder,
                    application_load_balancer=application_load_balancer,
                )

            except ValidationError as error:
                error_description = "Schema[{}] with value {}".format(
                    "][".join(error.absolute_schema_path), error.message
                )
                logging.warning(
                    logging_message.format(status_code=400, message=error_description)
                )
                error_tuple = ("Validation Error", 400)

            except Exception as error:
                if error_handler:
                    error_handler(error, method_name)
                else:
                    raise

        body, status_code = error_tuple
        return Response(body, status_code).to_json(
            application_load_balancer=application_load_balancer
        )

    def inner_handler(method_name, path="/", schema=None, load_json=True):
        if schema and not load_json:
            raise ValueError("if schema is supplied, load_json needs to be true")

        def wrapper(func):
            @wraps(func)
            def inner(event, *args, **kwargs):
                if load_json:
                    json_data = {
                        "body": json.loads(event.get("body") or "{}"),
                        "query": __json_load_query(event.get("queryStringParameters")),
                    }
                    event["json"] = json_data
                    if schema:
                        # jsonschema.validate using given schema
                        validate(json_data, schema, **__validate_kwargs)
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

    lambda_handler = inner_lambda_handler
    lambda_handler.handle = inner_handler
    return lambda_handler


# singleton
lambda_handler = create_lambda_handler()
