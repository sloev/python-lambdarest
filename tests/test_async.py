# pylint: disable-all
import pytest
import sys

@pytest.mark.skipif(sys.version_info < (3, 5, 2),
                                reason="requires python 3.5.2 or above")
def test_async_client_auth_and_get():
    import os
    from aioresponses import aioresponses
    import asyncio
    from trustpilot import async_client

    loop = asyncio.get_event_loop()

    with aioresponses() as m:
        m.get(
            'https://api.tp-staging.com/v1/foo/bar',
            status=401
        )
        m.post(
            'https://api.tp-staging.com/v1/oauth/oauth-business-users-for-applications/accesstoken',
            payload=dict(
                access_token="foobarbaz"
            )
        )
        m.get(
            'https://api.tp-staging.com/v1/foo/bar',
            payload=dict(
                foo='foobarbaz'
            )
        )

        session = async_client.TrustpilotAsyncSession(
            api_host='https://api.tp-staging.com',
            api_key='something',
            api_secret='secret',
            username='username',
            password='password'
        )

        async def get_response():
            response = await session.get('/v1/foo/bar')
            response_json = await response.json()
            assert response_json['foo'] == 'foobarbaz'
            assert session.access_token == 'foobarbaz'

        resp = loop.run_until_complete(get_response())
