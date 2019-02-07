# -*- coding: utf-8 -*-
import click
import json
import logging
import sys
import os.path as path
from inspect import getsourcefile


current_dir = path.dirname(path.abspath(getsourcefile(lambda: 0)))
sys.path.insert(0, current_dir[: current_dir.rfind(path.sep)])
logger = logging.getLogger(__name__)

from trustpilot import client, auth, __version__
from collections import OrderedDict


@click.pass_context
def get_verbosity(ctx):
    return ctx.meta.get("trustpilot.verbosity", 0)


def format_response(response):
    content = response.text
    try:
        content = response.json()
    except ValueError:
        pass
    output = OrderedDict()
    output["url"] = response.url
    output["status"] = response.status_code
    if get_verbosity():  # pylint: disable=E1120
        headers = response.headers
        output["headers"] = OrderedDict((k, headers[k]) for k in headers)
    output["content"] = content

    return json.dumps(output, indent=2)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--host', type=str, help="host name",
              envvar='TRUSTPILOT_API_HOST')
@click.option('--key', type=str, help="api key",
              envvar='TRUSTPILOT_API_KEY')
@click.option('--secret', type=str, help="api secret",
              envvar='TRUSTPILOT_API_SECRET')
@click.option('--token_issuer_host', type=str, default="",
              help="token issuer host name",
              envvar='TRUSTPILOT_API_TOKEN_ISSUER_HOST')
@click.option('--username', type=str, default="", help="Trustpilot username",
              envvar='TRUSTPILOT_USERNAME')
@click.option('--password', type=str, default="", help="Trustpilot password",
              envvar='TRUSTPILOT_PASSWORD')
@click.option('-c', type=str, help="json config file name")
@click.option('-v', '--verbose', count=True, help='verbosity level')
def cli(ctx, **kwargs):
    splash = r'''
         _____              _         _ _       _
        |_   _|            | |       (_) |     | |
          | |_ __ _   _ ___| |_ _ __  _| | ___ | |_
          | | '__| | | / __| __| '_ \| | |/ _ \| __|
          | | |  | |_| \__ \ |_| |_) | | | (_) | |_
          \_/_|   \__,_|___/\__| .__/|_|_|\___/ \__|
                               | |
                               |_|
          ___        _   _____ _ _            _
         / _ \      (_) /  __ \ (_)          | |
        / /_\ \_ __  _  | /  \/ |_  ___ _ __ | |_
        |  _  | '_ \| | | |   | | |/ _ \ '_ \| __|
        | | | | |_) | | | \__/\ | |  __/ | | | |_
        \_| |_/ .__/|_|  \____/_|_|\___|_| |_|\__|
              | |
              |_|   '''
    splash = click.style(splash, fg='green') + click.style(
        "v{}".format(__version__), fg='red') + "\n"

    values_dict = {}
    config_filename = kwargs.pop("c")

    if config_filename:
        with open(config_filename, "r") as f:
            values_dict = json.load(f)

    # setup verbosity level for global access
    verbosity = kwargs.get("verbose")
    ctx.meta["trustpilot.verbosity"] = verbosity

    # setup logging (increasing information levels)
    # _ : content, url, status_code
    # v : headers
    # vv: logging.INFO level
    # vvv: logging.DEBUG level
    levels = {
        2: logging.INFO,
        3: logging.DEBUG
    }
    logging_level = levels.get(verbosity, logging.CRITICAL)

    logger.setLevel(logging_level)
    if logging_level > logging.DEBUG:
        # disable urllib3 logging
        client.disable_ssl_warnings()

    if ctx.invoked_subcommand is None:
        click.echo("\n".join([splash, ctx.get_help()]))
        return

    # create default session
    try:
        client.create_session(
            api_host=kwargs.pop("host") or values_dict.get(
                "TRUSTPILOT_API_HOST") or "https://api.tp-staging.com",
            api_key=kwargs.pop("key") or values_dict["TRUSTPILOT_API_KEY"],
            api_secret=(kwargs.pop("secret")
                        or values_dict.get("TRUSTPILOT_API_SECRET", None)),
            token_issuer_host=(kwargs.pop("token_issuer_host") or
                               values_dict.get(
                                   "TRUSTPILOT_API_TOKEN_ISSUER_HOST", None)),
            username=kwargs.pop("username") or values_dict["TRUSTPILOT_USERNAME"],
            password=kwargs.pop("password") or values_dict["TRUSTPILOT_PASSWORD"]
        )
    except KeyError as key:
        raise SystemExit("Missing argument: {}".format(key))


cli_command = cli.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True
))


@cli_command
def create_access_token():
    '''
    Get an access token
    '''
    client.default_session.get_request_auth_headers()
    click.echo(client.default_session.access_token)


@cli_command
@click.argument('path')
def get(path):
    '''
    Send a GET request
    '''
    response = client.get(url=path)
    click.echo(format_response(response))


@cli_command
@click.argument('path')
@click.option('--data',  type=str, help="json_data to post")
@click.option('--content-type', type=str, default="application/json",
              help="content-type, default=application/json")
def post(path, data, content_type):
    '''
    Send a POST request with specified data
    '''
    headers = {
        'content-type': content_type
    }
    response = client.post(url=path, data=data, headers=headers)
    click.echo(format_response(response))


@cli_command
@click.argument('path')
def delete(path):
    '''
    Send a DELETE request
    '''
    response = client.delete(url=path)
    click.echo(format_response(response))


@cli_command
@click.argument('path')
@click.option('--data',  type=str, help="json_data to post")
@click.option('--content-type', type=str, default="application/json",
              help="content-type, default=application/json")
def put(path, data, content_type):
    '''
    Send a PUT request with specified data
    '''
    headers = {
        'content-type': content_type
    }
    response = client.put(url=path, data=data, headers=headers)
    click.echo(format_response(response))


if __name__ == "__main__":
    cli()  # pylint: disable=E1120
