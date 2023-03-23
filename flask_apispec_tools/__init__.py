from typing import NoReturn

from apispec import BasePlugin
from flask import Flask

from flask_apispec_tools.endpoints import Version, Docs, DocsJSON
from flask_apispec_tools.commands import generate_api_docs
from flask_apispec_tools.tools import config_value, CONFIG_SECTION


def init(
        app: Flask,
        *,
        docs_endpoint: str | bool = '/docs',
        docs_json_endpoint: str | bool = '/docs/json',
        version_endpoint: str | bool = '/version',
        plugins: list[BasePlugin] = None,
        config_values: dict[str, str] = None
) -> NoReturn:
    """
    Initialize flask-apispec-tools.

    Args:
        app: The Flask app to initialize flask-apispec-tools with.
        docs_endpoint: Set to False to disable this endpoint. Otherwise, sets the path for the endpoint that displays the docs with Swagger UI.
        docs_json_endpoint: Set to False to disable this endpoint. Otherwise, sets the path for the endpoint that returns the docs as JSON.
        version_endpoint: Set to False to disable this endpoint. Otherwise, sets the path for the endpoint the returns the API version.
        plugins: A list of apispec plugins to pass to the APISpec object.
        config_values: A dictionary of config values to set for flask_apispec_tools. Will override existing values.

    Returns:
        The Flask app that was originally passed in.
    """

    if CONFIG_SECTION not in app.config:
        app.config[CONFIG_SECTION] = {}

    if config_values is not None:
        app.config[CONFIG_SECTION].update(config_values)

    if plugins is not None:
        app.config[CONFIG_SECTION].update(
            {'plugins': plugins}
        )

    # validate config
    config_value('title', config=app.config)
    config_value('description', config=app.config)
    config_value('version', config=app.config)
    config_value('docs_dir', config=app.config)
    docs_type = config_value('docs_type', config=app.config)
    if docs_type not in ('json', 'yaml'):
        raise ValueError("[flask-apispec-tools] invalid config. docs_type must be either 'json' or 'yaml'")

    # register command
    app.cli.add_command(generate_api_docs)

    # add endpoints
    if docs_endpoint is not False:

        if docs_json_endpoint is False:
            raise ValueError('docs_json_endpoint can not be False when docs_endpoint is not False')

        app.add_url_rule(docs_endpoint,
                         view_func=Docs.as_view('flask_apispec_tools_docs'),
                         methods=['GET'])

    if docs_json_endpoint is not False:
        app.add_url_rule(docs_json_endpoint,
                         view_func=DocsJSON.as_view('flask_apispec_tools_docs_json'),
                         methods=['GET'])

    if version_endpoint is not False:
        app.add_url_rule(version_endpoint,
                         view_func=Version.as_view('flask_apispec_tools_version'),
                         methods=['GET'])
