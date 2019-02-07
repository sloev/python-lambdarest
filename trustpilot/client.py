# -*- coding: utf-8 -*-
import requests
import logging

from trustpilot import auth
from os import environ
from warnings import warn

logger = logging.getLogger(__name__)
_session_cache = {}


def disable_ssl_warnings():
    try:
        import requests.packages.urllib3
        urllib3_logger = logging.getLogger('requests')
        urllib3_logger.setLevel(logging.WARNING)
        urllib3_logger.propagate = False
        requests.packages.urllib3.disable_warnings()
        logger.info({
            "message": "Ssl warnings from urllib3 disabled! "
                       "(info: http://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings)"})
    except ImportError:
        logger.error("Error importing urllib3 when disabling its logging")


class TrustpilotSession(requests.Session):
    def __init__(self, **kwargs):
        super(TrustpilotSession, self).__init__()
        self.setup(**kwargs)
        self._pre_hooks = []
        self._post_hooks = []
        self.auth = self._pre_request_callback

    def setup(self, api_host=None, api_key=None, api_secret=None,
              username=None, password=None,
              access_token=None, token_issuer_path=None,
              token_issuer_host=None, **kwargs):

        self.api_host = api_host or environ.get('TRUSTPILOT_API_HOST', 'https://api.trustpilot.com')
        self.token_issuer_host = token_issuer_host or self.api_host
        self.access_token = access_token
        self.token_issuer_path = token_issuer_path or environ.get(
            'TRUSTPILOT_API_TOKEN_ISSUER_PATH', "oauth/oauth-business-users-for-applications/accesstoken")
        self.hooks = dict()

        if not self.api_host.startswith("http"):
            raise requests.URLRequired(
                "'{}' is not a valid api_host url".format(api_host))

        try:
            self.api_key=api_key or environ['TRUSTPILOT_API_KEY']
            self.api_secret=api_secret or environ.get('TRUSTPILOT_API_SECRET', '')
            self.username=username or environ.get('TRUSTPILOT_USERNAME')
            self.password=password or environ.get('TRUSTPILOT_PASSWORD')
            self.access_token=access_token
            self.hooks['response'] = self._post_request_callback
        except KeyError as e:
            logger.debug("Not auth setup, missing env-var or setup for {}".format(e))

        return self

    def get_request_auth_headers(self):
        url, data, headers = auth.create_access_token_request_params(self)
        response = requests.post(url=url, headers=headers, data=data)

        self.access_token = None
        if response and response.status_code == requests.codes["ok"]:
            response_json = response.json()
            self.access_token = response_json["access_token"]

        self.headers.update(dict(
            Authorization="Bearer {}".format(self.access_token),
            apikey=self.api_key
        ))
        return self.headers

    def _pre_request_callback(self, request):
        for hook in self._pre_hooks:
            hook(self, request)
        return request

    def _post_request_callback(self, response, *args, **kwargs):
        req = response.request
        retry = getattr(req, "authentication_retry", True)

        if retry and response.status_code == requests.codes.unauthorized:
            logger.debug({
                "message":"reauthenticating and retrying once",
                "url": req.url
            })
            req.authentication_retry = False
            req.headers.update(self.get_request_auth_headers())
            response = self.send(req)
        else:
            for hook in self._post_hooks:
                hook(self, response)

        return response

    def register_pre_hook(self, hook):
        self._pre_hooks.append(hook)

    def register_post_hook(self, hook):
        self._post_hooks.append(hook)

    def request(self, method, url, **kwargs):  # pylint: disable=W0221
        if not any(prefix in url for prefix in ["http://", "https://"]):
            url = "{}{}".format(self.api_host, url)
        return super(TrustpilotSession, self).request(method, url, **kwargs)


def get_session():
    warn("'trustpilot.client.get_session' is deprecated!, "
         "use trustpilot.client.default_session instead",
         DeprecationWarning)
    return default_session


def create_session(api_host=None, api_key=None, api_secret=None,
                   username=None, password=None,
                   access_token_path=None,
                   token_issuer_host=None, access_token=None):
    warn("'trustpilot.client.create_session' is deprecated!, "
         "use trustpilot.client.default_session.setup instead",
         DeprecationWarning)

    default_session.setup(
        api_host=api_host,
        api_key=api_key,
        api_secret=api_secret,
        access_token=access_token,
        token_issuer_path=access_token_path,
        token_issuer_host=token_issuer_host,
        username=username,
        password=password
    )

    return default_session


def post(url, data=None, json=None, **kwargs):
    return default_session.post(url, data=data, json=json, **kwargs)


def head(url, **kwargs):
    return default_session.head(url, **kwargs)


def options(url, **kwargs):
    return default_session.options(url, **kwargs)


def get(url, **kwargs):
    return default_session.get(url, **kwargs)


def patch(url, data=None, **kwargs):
    return default_session.patch(url, data=data, **kwargs)


def delete(url, **kwargs):
    return default_session.delete(url, **kwargs)


def put(url, data=None, **kwargs):
    return default_session.put(url, data, **kwargs)


default_session = TrustpilotSession()
