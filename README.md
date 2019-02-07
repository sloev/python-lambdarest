# trustpilot

[![Build Status](https://travis-ci.org/trustpilot/python-trustpilot.svg?branch=master)](https://travis-ci.org/trustpilot/python-trustpilot) [![Latest Version](https://img.shields.io/pypi/v/trustpilot.svg)](https://pypi.python.org/pypi/trustpilot) [![Python Support](https://img.shields.io/pypi/pyversions/trustpilot.svg)](https://pypi.python.org/pypi/trustpilot)

Python HTTP client for [Trustpilot](https://developers.trustpilot.com/).

### Features

* Extends the [`requests.Session`](http://docs.python-requests.org/en/master/api/#requests.Session) class with automatic authentication for public and private endpoints
* GET, POST, PUT, DELETE, HEAD, OPTIONS and PATCH methods are exposed on module level
* Implements session factory and default singleton session
* Provides a simple hook system
* CLI tool with basic HTTP commands

## Installation

Install the package from [PyPI](http://pypi.python.org/pypi/) using [pip](https://pip.pypa.io/):

```
pip install trustpilot
```

## Getting Started

This client is using the [Requests](http://docs.python-requests.org/en/master/) library. Responses are standard [`requests.Response`](http://docs.python-requests.org/en/master/api/#requests.Response) objects. You can use it as a factory or as a singleton.

### Use the singleton session

Use the built-in `default session` to instantiate a globally accessible session.

```python
from trustpilot import client
client.default_session.setup(
    api_host="https://api.trustpilot.com",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    username="YOUR_TRUSTPILOT_BUSINESS_USERNAME",
    password="YOUR_TRUSTPILOT_BUSINESS_PASSWORD"
)
response = client.get("/v1/foo/bar")
```

You can rely on environment variables for the setup of sessions so

```bash
$ env
TRUSTPILOT_API_HOST=foobar.com
TRUSTPILOT_API_KEY=foo
TRUSTPILOT_API_SECRET=bar
TRUSTPILOT_USERNAME=username
TRUSTPILOT_PASSWORD=password
```

Will work with the implicit `default_session` and the `TrustpilotSession.setup` method.

```python
from trustpilot import client
client.get("/v1/foo/bar")
```

### Instantiate your own session

You can create as many sessions as you like, as long as you pass them around yourself.

```python
from trustpilot import client
session = client.TrustpilotSession(
    api_host="https://api.trustpilot.com",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    username="YOUR_TRUSTPILOT_BUSINESS_USERNAME",
    password="YOUR_TRUSTPILOT_BUSINESS_PASSWORD"
)
response = session.get("/v1/foo/bar")
```

## Async client

Since version `3.0.0` you are able to use the `async_client` for `asyncio` usecases.

To use the default `async_client` session, using `env-vars` for settings, import is as following:

```python
import asyncio
from trustpilot import async_client
loop = asyncio.get_event_loop()

async def get_response():
    response = await async_client.get('/v1/foo/bar')
    response_json = await response.json()

loop.run_until_complete(get_response())
```

Or instantiate the session yourself with:

```python
import asyncio
from trustpilot import async_client
loop = asyncio.get_event_loop()

session = async_client.TrustpilotAsyncSession(
    api_host="https://api.trustpilot.com",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    username="YOUR_TRUSTPILOT_BUSINESS_USERNAME",
    password="YOUR_TRUSTPILOT_BUSINESS_PASSWORD"
)

async def get_response():
    response = await session.get('/v1/foo/bar')
    response_json = await response.json()

loop.run_until_complete(get_response())
```


## CLI

A command line tool `trustpilot_api_client` is bundled with the module. To invoke it, use:

```bash
Usage: trustpilot_api_client [OPTIONS] COMMAND [ARGS]...

Options:
  --host TEXT               host name
  --key TEXT                api key
  --secret TEXT             api secret
  --token_issuer_host TEXT  token issuer host name
  --username TEXT           Trustpilot username
  --password TEXT           Trustpilot password
  -c TEXT                   json config file name
  -v, --verbose             verbosity level
  --help                    Show this message and exit.

Commands:
  create_access_token  Get an access token
  delete               Send a DELETE request
  get                  Send a GET request
  post                 Send a POST request with specified data
  put                  Send a PUT request with specified data
```

In order to use the **-c** option please supply the filename of a JSON in the following format:

```json
{
  "TRUSTPILOT_API_HOST": "foo",
  "TRUSTPILOT_API_KEY": "bar",
  "TRUSTPILOT_API_SECRET": "baz",
  "TRUSTPILOT_USERNAME": "username",
  "TRUSTPILOT_PASSWORD": "password"
}
```

## Tests

You can use pytest to run tests against your current Python version. 

See [`setup.py`](setup.py) for test dependencies.
