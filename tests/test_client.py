try:
    from unittest import mock
except ImportError:
    import mock
import unittest
import responses
import json

from trustpilot import client


def assert_not_called(mock):
    assert mock.call_count == 0

def assert_called_once(mock):
    assert mock.call_count == 1


class TestCliMethods(unittest.TestCase):
    def setUp(self):
        self.api_host = "https://hostname.com"
        self.api_key = "secret_api_key"
        self.api_secret = "secret_api_secret"
        self.token_issuer_path = "oauth/oauth-business-users-for-applications/accesstoken"
        self.token_issuer_host = "https://hostname.com"
        self.username = "username"
        self.password = "password"

        self.request_url = "/v1/this/1"

        self.exp_headers = {
            'apikey': 'secret_api_key',
            'Authorization': 'Bearer access_token'}

    @property
    def session(self):
        session = client.default_session.setup(
            api_host=self.api_host,
            api_key=self.api_key,
            api_secret=self.api_secret,
            token_issuer_path=self.token_issuer_path,
            token_issuer_host=self.token_issuer_host,
            username=self.username,
            password=self.password
        )
        return session

    @mock.patch("trustpilot.client.auth", autospec=True)
    def test_deprecated_create_session(self, auth_mock):
        session = client.create_session(
            api_host=self.api_host,
            api_key=self.api_key,
            api_secret=self.api_secret,
            access_token_path=self.token_issuer_path,
            token_issuer_host=self.token_issuer_host,
            username=self.username,
            password=self.password
        )
        for attr in ["api_key",
                     "api_secret",
                     "api_host",
                     "token_issuer_path",
                     "token_issuer_host",
                     "username",
                     "password"]:
            assert getattr(self, attr) == getattr(session, attr)

    @responses.activate
    def test_get_public_endpoint_with_apikey_and_no_access_token(self):
        with responses.RequestsMock(
                assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="bar", status=200
            )

            session = client.default_session.setup(api_host=self.api_host)
            response = session.get(self.request_url)
            assert response.text == 'bar'
            assert response.status_code == 200

    @responses.activate
    def test_request_renew_auth_token_success(self):
        with responses.RequestsMock(
                assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.POST,
                'https://hostname.com/v1/oauth/oauth-business-users-for-applications/accesstoken',
                body='{"access_token":"access_token"}', status=200
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="foo", status=401
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="bar", status=200
            )

            session = self.session
            response = session.get(self.request_url)

            headers = dict(response.request.headers)

            assert response.text == "bar"
            assert all(value == headers[key] for key, value in self.exp_headers.items())

    @responses.activate
    def test_request_renew_auth_token_fail(self):
        with responses.RequestsMock(
                assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.POST,
                'https://hostname.com/v1/oauth/oauth-business-users-for-applications/accesstoken',
                body='go away', status=401
            )
            rsps.add(
                    responses.GET,
                    'https://hostname.com/v1/this/1',
                    body="bar",
                    status=401
            )
            rsps.add(
                    responses.GET,
                    'https://hostname.com/v1/this/1',
                    body="foo",
                    status=401
            )
            session = self.session
            response = session.get(self.request_url)

            assert response.text == "foo"


    @responses.activate
    def test_no_hooks(self):
        with responses.RequestsMock(
                assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.POST,
                'https://hostname.com/v1/oauth/oauth-business-users-for-applications/accesstoken',
                body='{"access_token":"access_token"}', status=200
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="foo", status=401
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="bar", status=200
            )
            session = self.session
            hook_mock = mock.Mock()

            # no hooks
            session.get(self.request_url)
            assert_not_called(hook_mock.pre_hook)
            assert_not_called(hook_mock.post_hook)

    @responses.activate
    def test_pre_hook(self):
        with responses.RequestsMock(
                assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.POST,
                'https://hostname.com/v1/oauth/oauth-business-users-for-applications/accesstoken',
                body='{"access_token":"access_token"}', status=200
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="foo", status=401
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="bar", status=200
            )
            session = self.session
            hook_mock = mock.Mock()

            session.register_pre_hook(hook_mock.pre_hook)

            session.get(self.request_url)

            assert_called_once(hook_mock.pre_hook)
            assert_not_called(hook_mock.post_hook)

    @responses.activate
    def test_post_hook(self):
        with responses.RequestsMock(
                assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.POST,
                'https://hostname.com/v1/oauth/oauth-business-users-for-applications/accesstoken',
                body='{"access_token":"access_token"}', status=200
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="foo", status=401
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="bar", status=200
            )
            session = self.session
            hook_mock = mock.Mock()

            session.register_post_hook(hook_mock.post_hook)
            session.get(self.request_url)
            assert_not_called(hook_mock.pre_hook)
            assert_called_once(hook_mock.post_hook)

    @responses.activate
    def test_pre_and_post_hooks(self):
        with responses.RequestsMock(
                assert_all_requests_are_fired=True) as rsps:
            rsps.add(
                responses.POST,
                'https://hostname.com/v1/oauth/oauth-business-users-for-applications/accesstoken',
                body='{"access_token":"access_token"}', status=200
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="foo", status=401
            )
            rsps.add(
                responses.GET,
                'https://hostname.com/v1/this/1',
                body="bar", status=200
            )
            session = self.session
            hook_mock = mock.Mock()

            session.register_pre_hook(hook_mock.pre_hook)
            session.register_post_hook(hook_mock.post_hook)

            session.get(self.request_url)

            assert_called_once(hook_mock.pre_hook)
            assert_called_once(hook_mock.post_hook)
