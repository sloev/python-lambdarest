# pylint: disable-all

try:
    import aiohttp
except ImportError:
    raise RuntimeError(
        "aiohttp is not installed, possibly running in python27?")
from logging import getLogger

logger = getLogger("trustpilot.async_client")

from os import environ
import base64
from trustpilot import auth


class TrustpilotAsyncSession():
    __SUPPORTED_HTTP_METHODS = [
        'post',
        'get',
        'put',
        'delete'
    ]

    def __init__(self, *args, **kwargs):
        self.setup(**kwargs)
        self.headers = {}

    def setup(self, api_host=None, api_key=None, api_secret=None,
              username=None, password=None,
              access_token=None, token_issuer_path=None,
              token_issuer_host=None, **kwargs):

        self.api_host = api_host or environ.get(
            'TRUSTPILOT_API_HOST', 'https://api.trustpilot.com')
        self.token_issuer_host = token_issuer_host or self.api_host
        self.access_token = access_token
        self.token_issuer_path = token_issuer_path or environ.get(
            'TRUSTPILOT_API_TOKEN_ISSUER_PATH', "oauth/oauth-business-users-for-applications/accesstoken")
        self.hooks = dict()

        if not self.api_host.startswith("http"):
            raise aiohttp.http_exceptions.InvalidURLError(
                "'{}' is not a valid api_host url".format(api_host))

        try:
            self.api_key = api_key or environ['TRUSTPILOT_API_KEY']
            self.api_secret = api_secret or environ.get(
                'TRUSTPILOT_API_SECRET', '')
            self.username=username or environ.get('TRUSTPILOT_USERNAME')
            self.password=password or environ.get('TRUSTPILOT_PASSWORD')
            self.access_token = access_token
        except KeyError as e:
            logger.debug(
                "Not auth setup, missing env-var or setup for {}".format(e))

        return self

    async def get_request_auth_headers(self):
        url, data, headers = auth.create_access_token_request_params(self)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                response_json = await response.json()
                self.access_token = response_json["access_token"]
                self.headers.update(dict(
                    Authorization="Bearer {}".format(self.access_token),
                    apikey=self.api_key
                ))

    async def authenticated_request(self, method, url, **kwargs):
        if method not in self.__SUPPORTED_HTTP_METHODS:
            raise RuntimeError("Http method {} not supported".format(method))
        if not any(prefix in url for prefix in ["http://", "https://"]):
            url = "{}{}".format(self.api_host, url)

        async with aiohttp.ClientSession(headers=self.headers) as session:
            http_method = getattr(session, method)
            response = await http_method(url, **kwargs)

        if response.status == 401:
            await self.get_request_auth_headers()
            async with aiohttp.ClientSession(headers=self.headers) as session:
                http_method = getattr(session, method)
                response = await http_method(url, **kwargs)
        return response

    async def post(self, url, *args, **kwargs):
        return await self.authenticated_request('post', url, *args, **kwargs)

    async def get(self, url, *args, **kwargs):

        return await self.authenticated_request('get', url, *args, **kwargs)

    async def put(self, url, *args, **kwargs):
        return await self.authenticated_request('put', url, *args, **kwargs)

    async def delete(self, url, *args, **kwargs):
        return await self.authenticated_request('delete', url, *args, **kwargs)


default_session = TrustpilotAsyncSession()
get = default_session.get
post = default_session.post
put = default_session.put
delete = default_session.delete
