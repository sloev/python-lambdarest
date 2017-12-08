try:
    from unittest import mock
except ImportError:
    import mock

import unittest
import json
import copy

from lambdarest import create_lambda_handler

def assert_not_called(mock):
    assert mock.call_count == 0

def assert_called_once(mock):
    assert mock.call_count == 1


class TestLambdarestFunctions(unittest.TestCase):
    def setUp(self):
        self.event = {
          "resource": "/test",
          "path": "/",
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
              "user": "asdfsadsfads"
            },
            "resourcePath": "/test",
            "httpMethod": "POST",
            "apiId": "90o718c6bk"
          },
          "body": None,
          "isBase64Encoded": False
        }
        self.context = {
            "foo": "bar"
        }
        self.lambda_handler = create_lambda_handler()

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
                        end="2017-01-31T23:06:37.831Z"
                    ),
                    dict(
                        key="segment-logz/abcde/asdfg/5678.gz",
                        start="2017-01-31T20:06:46.102Z",
                        end="2017-01-31T21:06:37.831Z"
                    )
                ],
                schema='{"foo":"bar"}',
                iam="sadfasdf",
                start="2017-01-31T20:06:46.102Z",
                end="2017-01-31T23:06:37.831Z"
                )
            ]
        )
        self.event["body"] = json.dumps(json_body)
        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = dict(
            body=json_body,
            query={}
        )

        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        assert result == {"body": '"foo"', "statusCode": 200, "headers": {}}
        post_mock.assert_called_with(assert_event)

    def test_schema_valid(self):
        json_body = dict(
            foo="hej",
            time="2017-01-31T21:06:37.831Z"
        )
        post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "foo": {
                    "type": "string"
                },
                "time": {
                    "type": "string",
                    "format": "date-time"

                }
            }
        }

        self.event["body"] = json.dumps(json_body)
        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = dict(
            body=json_body,
            query={}
        )
        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post" , schema=post_schema)(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        assert result == {"body": '"foo"', "statusCode": 200, "headers": {}}
        post_mock.assert_called_with(assert_event)

    def test_schema_invalid(self):
        json_body = dict(
            my_integer="this is not an integer",
        )
        post_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "body": {
                    "type": "object",
                    "properties": {
                        "my_integer": {
                            "type": "integer"
                        }
                    }
                }
            }
        }

        self.event["body"] = json.dumps(json_body)
        # create deep copy for testing purposes, self.event is mutable
        assert_event = copy.deepcopy(self.event)
        assert_event["context"] = self.context
        assert_event["json"] = dict(
            body=json_body,
            query={}
        )
        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post", schema=post_schema)(
            post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        assert result == {"body": '"Validation Error"', "statusCode": 400, "headers": {}}

    def test_that_it_returns_bad_request_if_not_given_lambda_proxy_input(self):
        json_body = dict(
            my_integer="this is not an integer",
        )

        event = json.dumps(json_body)

        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(event, self.context)
        assert result == {
            "body": '"Bad request, maybe not using Lambda Proxy?"',
            "statusCode": 500,
            "headers": {}}


    def test_that_it_unpacks_and_validates_query_params(self):
        json_body = dict(
            my_integer="this is not an integer",
        )
        queryStringParameters = dict(
            foo='"keys"',
            bar="{\"baz\":20}",
            baz='1,2,3',
            apples="1"
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
                        "foo": {
                            "type": "string"
                        },
                        "bar": {
                            "type": "object",
                            "properties": {
                                "baz": {"type": "number"}
                            }
                        },
                        "baz": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            }
                        },
                        "apples": {
                            "type": "number"
                        }
                    }
                }
            }
        }
        self.lambda_handler.handle("post", schema=post_schema)(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        assert result == {"body": '"foobar"', "statusCode": 200, "headers": {}}


    def test_that_it_works_without_body_or_queryStringParameters(self):
        post_mock = mock.Mock(return_value="foo")
        self.lambda_handler.handle("post")(post_mock)  # decorate mock
        result = self.lambda_handler(self.event, self.context)
        assert result == {'body': '"foo"', 'headers': {}, 'statusCode': 200}

    def test_that_specified_path_works(self):
        json_body = {}

        self.event["body"] = json.dumps(json_body)
        self.event["httpMethod"] = "GET"

        get_mock1 = mock.Mock(return_value="foo")
        get_mock2 = mock.Mock(return_value="bar")

        self.lambda_handler.handle("get", path="/foo/bar")(get_mock1)  # decorate mock
        self.lambda_handler.handle("get", path="/bar/foo")(get_mock2)  # decorate mock

        self.event["path"] = "/foo/bar"
        result1 = self.lambda_handler(self.event, self.context)
        assert result1 == {
            "body": '"foo"',
            "statusCode": 200,
            "headers": {}}

        self.event["path"] = "/bar/foo"
        result2 = self.lambda_handler(self.event, self.context)
        assert result2 == {
            "body": '"bar"',
            "statusCode": 200,
            "headers": {}}
