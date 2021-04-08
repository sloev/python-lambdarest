try:
    from unittest import mock
except ImportError:
    import mock

import copy
import json
import random
import time
import unittest
import base64
from datetime import datetime

from lambdarest import create_lambda_handler


def assert_not_called(mock):
    assert mock.call_count == 0


def assert_called_once(mock):
    assert mock.call_count == 1


class TestLambdarestFunctions(unittest.TestCase):
    def setUp(self):
        self.event = {
            "resource": "/",
            "httpMethod": "POST",
            "headers": None,
            "queryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "accountId": "1234123542134",
                "resourceId": "erd49w",
                "stage": "test-invoke-stage",
                "requestId": "test-invoke-request",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": "23424534543",
                    "cognitoIdentityId": None,
                    "caller": "asdfasdfasfdasfdas",
                    "apiKey": "asdfasdfasdfas",
                    "sourceIp": "127.0.0.1",
                    "accessKey": "asdfasdfasdfasfd",
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": "arn:aws:iam::123214323",
                    "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_102)",
                    "user": "asdfsadsfads",
                },
                "resourcePath": "/test",
                "httpMethod": "POST",
                "apiId": "90o718c6bk",
            },
            "body": None,
            "isBase64Encoded": False,
        }
        self.context = {"foo": "bar"}
        self.lambda_handler = create_lambda_handler()
        self.lambda_handler_application_load_balancer = create_lambda_handler(
            application_load_balancer=True
        )

    def test_post_validation_success(self):
        json_body = dict(
            items=[
                dict(
                    source="segment",
                    ingestion="segment s3 integration",
                    project_id="segment-logs/abcde",
                    data_container="gzip",
                    data_format="json",
                    data_state="raw",
                    files=[
                        dict(
                            key="segment-logz/abcde/asdf/1234.gz",
                            start="2017-01-31T22:06:46.102Z",
                            end="2017-01-31T23:06:37.831Z",
                        ),
                        dict(
                            key="segment-logz/abcde/asdfg/5678.gz",
                            start="2017-01-31T20:06:46.102Z",
                            end="2017-01-31T21:06:37.831Z",
                        ),
                    ],
                    schema='{"foo":"bar"}',
                    iam="sadfasdf",
                    start="2017-01-31T20:06:46.102Z",
                    end="2017-01-31T23:06:37.831Z",
                )
            ]
        )
        self.event["body"] = json.dumps(json_body)
        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = dict(body=json_body, query={})

        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(result, {"body": "foo", "statusCode": 200, "headers": {}})
        post_mock.assert_called_with(assert_event)

    def test_schema_valid(self):
        json_body = dict(foo="hej", time="2017-01-31T21:06:37.831Z")
        post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "foo": {"type": "string"},
                "time": {"type": "string", "format": "date-time"},
            },
        }

        self.event["body"] = json.dumps(json_body)
        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = dict(body=json_body, query={})
        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post", schema=post_schema)(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(result, {"body": "foo", "statusCode": 200, "headers": {}})
        post_mock.assert_called_with(assert_event)

    def test_schema_invalid(self):
        json_body = dict(my_integer="this is not an integer")
        post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "body": {
                    "type": "object",
                    "properties": {"my_integer": {"type": "integer"}},
                }
            },
        }

        self.event["body"] = json.dumps(json_body)
        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = dict(body=json_body, query={})
        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post", schema=post_schema)(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            result, {"body": "Validation Error", "statusCode": 400, "headers": {}}
        )

    def test_schema_with_oneof_invalid(self):
        json_body = dict(typeA="foobar")
        post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "body": {
                    "type": "object",
                    "oneOf": [
                        {"$ref": "#/definitions/typeA"},
                        {"$ref": "#/definitions/typeB"},
                    ],
                }
            },
            "definitions": {
                "typeA": {
                    "properties": {"propertyA": {"type": "string"}},
                    "required": ["propertyA"],
                },
                "typeB": {
                    "properties": {"propertyB": {"type": "string"}},
                    "required": ["propertyB"],
                },
            },
        }

        self.event["body"] = json.dumps(json_body)
        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = dict(body=json_body, query={})
        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post", schema=post_schema)(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            result, {"body": "Validation Error", "statusCode": 400, "headers": {}}
        )

    def test_that_it_returns_bad_request_if_not_given_lambda_proxy_input(self):
        json_body = dict(my_integer="this is not an integer")

        event = json.dumps(json_body)

        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(event, self.context)
        self.assertEqual(
            result,
            {
                "body": "Bad request, maybe not using Lambda Proxy?",
                "statusCode": 500,
                "headers": {},
            },
        )

    def test_that_it_unpacks_and_validates_query_params_and_raises_validation_error(
        self,
    ):
        """
        Deprecated behavior in v.10.0.1
        We are no longer supporting json objects as query params, please use json_body for that instead.
        in the following case we are not unpacking the query-arg-json-objects so they can be
        validated against the schema which means you will compare a string to a dictionary and
        get a validation error.
        """
        json_body = dict(my_integer="this is not an integer")
        queryStringParameters = dict(
            foo='"keys"', bar='{"baz":20}', baz="1,2,3", apples="1"
        )

        self.event["body"] = json.dumps(json_body)
        self.event["queryStringParameters"] = queryStringParameters

        def side_effect(event):
            return "foobar"

        post_mock = mock.MagicMock(side_effect=side_effect)

        post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "query": {  # here we adress the unpacked query params
                    "type": "object",
                    "properties": {
                        "foo": {"type": "string"},
                        "bar": {
                            "type": "object",
                            "properties": {"baz": {"type": "number"}},
                        },
                        "baz": {"type": "array", "items": {"type": "number"}},
                        "apples": {"type": "number"},
                    },
                }
            },
        }
        self.lambda_handler.handle("post", schema=post_schema)(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            result, {"body": "Validation Error", "headers": {}, "statusCode": 400}
        )

    def test_that_it_works_without_body_or_queryStringParameters(self):
        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(result, {"body": "foo", "headers": {}, "statusCode": 200})

    def test_that_it_works_with_empty_dict_and_status_code_as_response(self):
        post_mock = mock.Mock(return_value=({}, 200))
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(result, {"body": "{}", "headers": {}, "statusCode": 200})

    def test_that_specified_path_works(self):
        json_body = {}

        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "GET"

        get_mock1 = mock.Mock(return_value="foo")
        get_mock2 = mock.Mock(return_value="bar")

        self.lambda_handler.handle("get", path="/foo/bar")(get_mock1)  # decorate mock
        self.lambda_handler.handle("get", path="/bar/foo")(get_mock2)  # decorate mock

        self.event["resource"] = "/foo/bar"
        result1 = self.lambda_handler(self.event, self.context)
        self.assertEqual(result1, {"body": "foo", "statusCode": 200, "headers": {}})

        self.event["resource"] = "/bar/foo"
        result2 = self.lambda_handler(self.event, self.context)
        self.assertEqual(result2, {"body": "bar", "statusCode": 200, "headers": {}})

    def test_that_apigw_with_basepath_works(self):
        json_body = {}

        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "GET"

        get_mock1 = mock.Mock(return_value="foo")

        self.lambda_handler.handle("get", path="/foo/bar")(get_mock1)  # decorate mock

        self.event["path"] = "/v1/foo/bar"
        self.event["resource"] = "/foo/bar"
        result1 = self.lambda_handler(self.event, self.context)
        self.assertEqual(result1, {"body": "foo", "statusCode": 200, "headers": {}})

    def test_that_uppercase_works(self):
        json_body = {}

        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "GET"

        def test_wordcase(request, foo):
            return foo

        self.lambda_handler.handle("get", path="/foo/bar/<string:foo>")(
            test_wordcase
        )  # decorate mock

        self.event["resource"] = "/foo/bar/foobar"
        result1 = self.lambda_handler(self.event, self.context)
        self.assertEqual(result1, {"body": "foobar", "statusCode": 200, "headers": {}})

        self.event["resource"] = "/foo/bar/FOOBAR"
        result2 = self.lambda_handler(self.event, self.context)
        self.assertEqual(result2, {"body": "FOOBAR", "statusCode": 200, "headers": {}})

    def test_that_apigw_with_proxy_param_works(self):
        json_body = {}

        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "GET"

        get_mock1 = mock.Mock(return_value="foo")

        self.lambda_handler.handle("get", path="/foo/<path:path>")(
            get_mock1
        )  # decorate mock

        self.event["path"] = "/v1/foo/foobar"
        self.event["pathParameters"] = {"proxy": "foobar"}
        self.event["resource"] = "/foo/{proxy+}"
        result1 = self.lambda_handler(self.event, self.context)
        self.assertEqual(result1, {"body": "foo", "statusCode": 200, "headers": {}})

    def test_that_no_path_specified_match_all(self):
        random.seed(time.mktime(datetime.now().timetuple()))

        json_body = {}
        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "PUT"

        get_mock = mock.Mock(return_value="foo")

        self.lambda_handler.handle("put", path="*")(get_mock)

        r = range(1000)
        for i in range(10):
            # test with a non-deterministic path
            self.event["resource"] = "/foo/{}/".format(random.choice(r))
            result = self.lambda_handler(self.event, self.context)
            self.assertEqual(result, {"body": "foo", "statusCode": 200, "headers": {}})

    def test_exception_in_handler_should_be_reraised(self):
        json_body = {}
        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "GET"
        self.event["resource"] = "/foo/bar"

        def divide_by_zero(_):
            return 1 / 0

        self.lambda_handler = create_lambda_handler(error_handler=None)
        self.lambda_handler.handle("get", path="/foo/bar")(divide_by_zero)

        with self.assertRaises(ZeroDivisionError):
            self.lambda_handler(self.event, self.context)

    def test_that_alb_param_parm_works(self):
        json_body = {}

        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "GET"
        self.event["queryStringParameters"] = {}
        self.event["headers"] = {}
        del self.event["resource"]
        del self.event["stageVariables"]

        def mock_handler(event, id):
            return "foo:" + id

        get_mock1 = mock.Mock(wraps=mock_handler)

        self.lambda_handler_application_load_balancer.handle(
            "get", path="/foo/<id>/bar"
        )(
            get_mock1
        )  # decorate mock

        self.event["path"] = "/foo/foobar/bar"
        result1 = self.lambda_handler_application_load_balancer(
            self.event, self.context
        )
        self.assertEqual(
            result1,
            {
                "body": "foo:foobar",
                "statusCode": 200,
                "headers": {},
                "statusDescription": "HTTP OK",
                "isBase64Encoded": False,
            },
        )

    def test_that_alb_base64_encoding_works(self):
        json_body = {}

        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "GET"
        self.event["queryStringParameters"] = {}
        self.event["headers"] = {}
        del self.event["resource"]
        del self.event["stageVariables"]

        def mock_handler(event, id):
            return {
                "statusCode": 200,
                "body": base64.b64encode(
                    "test of base64 encoding for ALB".encode("utf8")
                ).decode("utf-8"),
                "isBase64Encoded": True,
                "headers": {"Content-Type": "text/plain"},
            }

        get_mock1 = mock.Mock(wraps=mock_handler)

        self.lambda_handler_application_load_balancer.handle(
            "get", path="/foo/<id>/bar"
        )(
            get_mock1
        )  # decorate mock

        self.event["path"] = "/foo/foobar/bar"
        result1 = self.lambda_handler_application_load_balancer(
            self.event, self.context
        )
        self.assertEqual(
            result1,
            {
                "body": "dGVzdCBvZiBiYXNlNjQgZW5jb2RpbmcgZm9yIEFMQg==",
                "statusCode": 200,
                "headers": {"Content-Type": "text/plain"},
                "statusDescription": "HTTP OK",
                "isBase64Encoded": True,
            },
        )

    def test_placeholder_filling(self):
        def my_own_get(_, object_id, foo):
            return [{"object_id": int(object_id)}, {"foo": foo}]

        self.lambda_handler.handle(
            "get", path="/object/<int:object_id>/props/<string:foo>/get"
        )(my_own_get)
        ##### TEST #####

        input_event = {
            "body": "{}",
            "httpMethod": "GET",
            "path": "/v1/object/777/props/bar/get",
            "resource": "/object/{object_id}/props/{foo}/get",
            "pathParameters": {"object_id": "777", "foo": "bar"},
        }
        result = self.lambda_handler(event=input_event)
        assert result == {
            "body": '[{"object_id": 777}, {"foo": "bar"}]',
            "statusCode": 200,
            "headers": {},
        }

    def test_incomplete_placeholder_filling(self):
        def my_own_get_1(_, object_id, foo):
            return [{"object_id": int(object_id)}, {"foo": foo}]

        self.lambda_handler.handle(
            "get", path="/incomplete_object/<int:object_id>/props/<string:foo>/get"
        )(my_own_get_1)
        ##### TEST #####

        input_event = {
            "body": "{}",
            "httpMethod": "GET",
            "path": "/v1/object/777/props/bar/get",
            "resource": "/object/{object_id}/props/{foo}/get",
            "pathParameters": {"object_id": "777"},
        }
        result = self.lambda_handler(event=input_event)

        assert result["statusCode"] == 404

    def test_that_html_is_not_surrounded_by_double_quotes(self):
        post_mock = mock.Mock(
            return_value="<html><head></head><body>Hello world!</body></html>"
        )
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            result,
            {
                "body": "<html><head></head><body>Hello world!</body></html>",
                "headers": {},
                "statusCode": 200,
            },
        )

    def test_that_standard_dict_responses_are_returned_as_is(self):
        post_mock = mock.Mock(
            return_value={"body": "something went wrong", "statusCode": 500}
        )
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            result, {"body": "something went wrong", "headers": {}, "statusCode": 500}
        )

    def test_that_standard_dict_responses_without_a_body_are_returned_as_is(self):
        post_mock = mock.Mock(
            return_value={
                "statusCode": 302,
                "headers": {"Location": "https://example.com"},
            }
        )
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            result, {"headers": {"Location": "https://example.com"}, "statusCode": 302}
        )

    def test_that_standard_dict_responses_without_a_body_are_returned_as_is_multiHeader(
        self,
    ):
        post_mock = mock.Mock(
            return_value={
                "statusCode": 302,
                "multiValueHeaders": {"Location": ["https://example.com"]},
            }
        )
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            result,
            {
                "multiValueHeaders": {"Location": ["https://example.com"]},
                "statusCode": 302,
            },
        )

    def test_that_dict_responses_that_happen_to_have_a_body_key_retain_previous_behavior(
        self,
    ):
        post_mock = mock.Mock(
            return_value={"foo": "bar", "body": "hurts", "more": "data"}
        )
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            json.loads(result["body"]), {"foo": "bar", "body": "hurts", "more": "data"}
        )
        self.assertEqual(result["headers"], {})
        self.assertEqual(result["statusCode"], 200)

    def test_that_json_encoding_body_list(self):
        post_mock = mock.Mock(return_value=[{"foo": "bar"}])
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(json.loads(result["body"]), [{"foo": "bar"}])
        self.assertEqual(result["headers"], {})
        self.assertEqual(result["statusCode"], 200)

    # test matrix for scopes
    #                     Scopes requested
    #                   none | single | multiple
    # Scopes provided:
    #         missing        |        |   A
    #            none    B   |        |
    #          single        |   C    |
    #        multiple    D   |        |   E
    #         invalid    F   |   G    |

    def test_scopes_A(self):
        post_mock = mock.Mock(return_value=[{"foo": "bar"}])
        self.lambda_handler.handle(
            "post", scopes=["resource.method1", "resource3.method2"]
        )(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(
            result, {"body": "Permission denied", "statusCode": 403, "headers": {}}
        )

    def test_scopes_B(self):
        event_with_empty_scopes = {
            "resource": "/",
            "httpMethod": "POST",
            "headers": None,
            "queryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "accountId": "1234123542134",
                "authorizer": {"scopes": "[]"},
                "resourceId": "erd49w",
                "stage": "test-invoke-stage",
                "requestId": "test-invoke-request",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": "23424534543",
                    "cognitoIdentityId": None,
                    "caller": "asdfasdfasfdasfdas",
                    "apiKey": "asdfasdfasdfas",
                    "sourceIp": "127.0.0.1",
                    "accessKey": "asdfasdfasdfasfd",
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": "arn:aws:iam::123214323",
                    "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_102)",
                    "user": "asdfsadsfads",
                },
                "resourcePath": "/test",
                "httpMethod": "POST",
                "apiId": "90o718c6bk",
            },
            "body": None,
            "isBase64Encoded": False,
        }
        post_mock = mock.Mock(return_value=[{"foo": "bar"}])
        self.lambda_handler.handle(
            "post", scopes=["resource.method1", "resource3.method2"]
        )(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(event_with_empty_scopes, self.context)
        self.assertEqual(
            result, {"body": "Permission denied", "statusCode": 403, "headers": {}}
        )

    def test_scopes_C(self):
        event_with_single_scope = {
            "resource": "/",
            "httpMethod": "POST",
            "headers": None,
            "queryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "accountId": "1234123542134",
                "authorizer": {"scopes": '["resource1.method2"]'},
                "resourceId": "erd49w",
                "stage": "test-invoke-stage",
                "requestId": "test-invoke-request",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": "23424534543",
                    "cognitoIdentityId": None,
                    "caller": "asdfasdfasfdasfdas",
                    "apiKey": "asdfasdfasdfas",
                    "sourceIp": "127.0.0.1",
                    "accessKey": "asdfasdfasdfasfd",
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": "arn:aws:iam::123214323",
                    "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_102)",
                    "user": "asdfsadsfads",
                },
                "resourcePath": "/test",
                "httpMethod": "POST",
                "apiId": "90o718c6bk",
            },
            "body": None,
            "isBase64Encoded": False,
        }
        post_mock = mock.Mock(return_value=[{"foo": "bar"}])
        self.lambda_handler.handle("post", scopes=["resource1.method2"])(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(event_with_single_scope, self.context)
        self.assertEqual(
            result, {"body": '[{"foo": "bar"}]', "statusCode": 200, "headers": {}}
        )

    def test_scopes_D(self):
        event_with_multiple_scopes = {
            "resource": "/",
            "httpMethod": "POST",
            "headers": None,
            "queryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "accountId": "1234123542134",
                "authorizer": {"scopes": '["resource1.method2", "resouce2.method3"]'},
                "resourceId": "erd49w",
                "stage": "test-invoke-stage",
                "requestId": "test-invoke-request",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": "23424534543",
                    "cognitoIdentityId": None,
                    "caller": "asdfasdfasfdasfdas",
                    "apiKey": "asdfasdfasdfas",
                    "sourceIp": "127.0.0.1",
                    "accessKey": "asdfasdfasdfasfd",
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": "arn:aws:iam::123214323",
                    "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_102)",
                    "user": "asdfsadsfads",
                },
                "resourcePath": "/test",
                "httpMethod": "POST",
                "apiId": "90o718c6bk",
            },
            "body": None,
            "isBase64Encoded": False,
        }
        post_mock = mock.Mock(return_value=[{"foo": "bar"}])
        self.lambda_handler.handle("post", scopes=[])(post_mock)  # decorate mock
        result = self.lambda_handler(event_with_multiple_scopes, self.context)
        self.assertEqual(
            result, {"body": '[{"foo": "bar"}]', "statusCode": 200, "headers": {}}
        )

    def test_scopes_E(self):
        event_with_multiple_scopes = {
            "resource": "/",
            "httpMethod": "POST",
            "headers": None,
            "queryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "accountId": "1234123542134",
                "authorizer": {"scopes": '["resource1.method2", "resouce2.method3"]'},
                "resourceId": "erd49w",
                "stage": "test-invoke-stage",
                "requestId": "test-invoke-request",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": "23424534543",
                    "cognitoIdentityId": None,
                    "caller": "asdfasdfasfdasfdas",
                    "apiKey": "asdfasdfasdfas",
                    "sourceIp": "127.0.0.1",
                    "accessKey": "asdfasdfasdfasfd",
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": "arn:aws:iam::123214323",
                    "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_102)",
                    "user": "asdfsadsfads",
                },
                "resourcePath": "/test",
                "httpMethod": "POST",
                "apiId": "90o718c6bk",
            },
            "body": None,
            "isBase64Encoded": False,
        }
        post_mock = mock.Mock(return_value=[{"foo": "bar"}])
        self.lambda_handler.handle(
            "post", scopes=["resouce2.method3", "resouce3.method1"]
        )(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(event_with_multiple_scopes, self.context)
        self.assertEqual(
            result, {"body": "Permission denied", "statusCode": 403, "headers": {}}
        )

    def test_scopes_F(self):
        event_with_invalid_scopes = {
            "resource": "/",
            "httpMethod": "POST",
            "headers": None,
            "queryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "accountId": "1234123542134",
                "authorizer": {"scopes": "{[invalid json}"},
                "resourceId": "erd49w",
                "stage": "test-invoke-stage",
                "requestId": "test-invoke-request",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": "23424534543",
                    "cognitoIdentityId": None,
                    "caller": "asdfasdfasfdasfdas",
                    "apiKey": "asdfasdfasdfas",
                    "sourceIp": "127.0.0.1",
                    "accessKey": "asdfasdfasdfasfd",
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": "arn:aws:iam::123214323",
                    "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_102)",
                    "user": "asdfsadsfads",
                },
                "resourcePath": "/test",
                "httpMethod": "POST",
                "apiId": "90o718c6bk",
            },
            "body": None,
            "isBase64Encoded": False,
        }
        post_mock = mock.Mock(return_value=[{"foo": "bar"}])
        self.lambda_handler.handle("post", scopes=[])(post_mock)  # decorate mock
        result = self.lambda_handler(event_with_invalid_scopes, self.context)
        self.assertEqual(
            result, {"body": '[{"foo": "bar"}]', "statusCode": 200, "headers": {}}
        )

    def test_scopes_G(self):
        event_with_invalid_scopes = {
            "resource": "/",
            "httpMethod": "POST",
            "headers": None,
            "queryStringParameters": None,
            "pathParameters": None,
            "stageVariables": None,
            "requestContext": {
                "accountId": "1234123542134",
                "authorizer": {"scopes": "{[invalid json}"},
                "resourceId": "erd49w",
                "stage": "test-invoke-stage",
                "requestId": "test-invoke-request",
                "identity": {
                    "cognitoIdentityPoolId": None,
                    "accountId": "23424534543",
                    "cognitoIdentityId": None,
                    "caller": "asdfasdfasfdasfdas",
                    "apiKey": "asdfasdfasdfas",
                    "sourceIp": "127.0.0.1",
                    "accessKey": "asdfasdfasdfasfd",
                    "cognitoAuthenticationType": None,
                    "cognitoAuthenticationProvider": None,
                    "userArn": "arn:aws:iam::123214323",
                    "userAgent": "Apache-HttpClient/4.5.x (Java/1.8.0_102)",
                    "user": "asdfsadsfads",
                },
                "resourcePath": "/test",
                "httpMethod": "POST",
                "apiId": "90o718c6bk",
            },
            "body": None,
            "isBase64Encoded": False,
        }
        post_mock = mock.Mock(return_value=[{"foo": "bar"}])
        self.lambda_handler.handle("post", scopes=["resource1.method2"])(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(event_with_invalid_scopes, self.context)
        self.assertEqual(
            result, {"body": "Permission denied", "statusCode": 403, "headers": {}}
        )

    def test_multiple_digit_account_ids_in_query_param_full_schema(self):
        post_schema = post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "query": {  # here we adress the unpacked query params
                    "type": "object",
                    "properties": {
                        "AccountId": {"type": "array", "items": {"type": "string"}}
                    },
                }
            },
        }
        self.event["queryStringParameters"] = {
            "AccountId": "123124124,0000000123123,0001fd,fd001,     fd012312,      000123"
        }
        self.event["body"] = ""

        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = {
            "body": {},
            "query": {
                "AccountId": [
                    "123124124",
                    "0000000123123",
                    "0001fd",
                    "fd001",
                    "     fd012312",
                    "      000123",
                ]
            },
        }

        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post", schema=post_schema)(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(result, {"body": "foo", "statusCode": 200, "headers": {}})
        call_args = post_mock.call_args_list[0][0][0]
        print("called with", json.dumps(call_args["json"], indent=2))
        print(
            "should have been called with", json.dumps(assert_event["json"], indent=2)
        )

        post_mock.assert_called_with(assert_event)

    def test_multiple_digit_account_ids_in_query_param_missing_schema_default_to_string(
        self,
    ):
        post_schema = post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {},
        }
        self.event["queryStringParameters"] = {
            "AccountId": "123124124,0000000123123,0001fd,fd001,     fd012312,      000123"
        }
        self.event["body"] = ""

        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = {
            "body": {},
            "query": {
                "AccountId": "123124124,0000000123123,0001fd,fd001,     fd012312,      000123"
            },
        }

        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post", schema=post_schema)(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(result, {"body": "foo", "statusCode": 200, "headers": {}})
        call_args = post_mock.call_args_list[0][0][0]
        print("called with", json.dumps(call_args["json"], indent=2))
        print(
            "should have been called with", json.dumps(assert_event["json"], indent=2)
        )

        post_mock.assert_called_with(assert_event)

    def test_query_param_schema_integer(self):
        post_schema = post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "query": {  # here we adress the unpacked query params
                    "type": "object",
                    "properties": {"myInteger": {"type": "integer"}},
                }
            },
        }
        self.event["queryStringParameters"] = {"myInteger": "0012"}
        self.event["body"] = ""

        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = {
            "body": {},
            "query": {"myInteger": 12},
        }

        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post", schema=post_schema)(
            post_mock
        )  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        self.assertEqual(result, {"body": "foo", "statusCode": 200, "headers": {}})
        call_args = post_mock.call_args_list[0][0][0]
        print("called with", json.dumps(call_args["json"], indent=2))
        print(
            "should have been called with", json.dumps(assert_event["json"], indent=2)
        )

        post_mock.assert_called_with(assert_event)

    def test_invalid_json(self):
        self.event["body"] = "{invalid:json}"
        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post")(post_mock)
        result = self.lambda_handler(self.event, self.context)
        assert result["statusCode"] == 400
        assert result["body"] == "Invalid json body"
