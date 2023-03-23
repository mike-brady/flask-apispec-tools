import os
import re

from apispec import APISpec, BasePlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, current_app, Config

CONFIG_SECTION = 'FLASK_APISPEC_TOOLS'


def get_api_spec(
        app: Flask = None,
        *,
        plugins: list[BasePlugin] = None,
        get_everything: bool = False,
        openapi_version: str = '3.0.3'
) -> tuple[APISpec, str]:
    """

    Args:
        app: Optional. Default: flask.current_app
        plugins: Optional. A list apispec Plugins. FlaskPlugin does not need to be included here. It will be used automatically.
        get_everything: Optional. When set, include all endpoints in the spec, even when marked "Exclude From Spec"
        openapi_version: Optional. The version of OpenAPI to use.

    Returns:
        An APISpec object and the version number of the API.
    """
    if app is None:
        app = current_app

    if plugins is None:
        plugins = []

    version = config_value('version', config=app.config)

    spec = APISpec(
        title=config_value('title', config=app.config),
        version=version,
        openapi_version=openapi_version,
        info={
            'description': config_value('description', config=app.config)
        },
        plugins=[FlaskPlugin(), *plugins]
    )

    with app.test_request_context():
        for view in app.view_functions:
            if view == 'static':
                continue
            view_doc = app.view_functions[view].view_class.__doc__ or ''
            if get_everything or not view_doc.startswith('Exclude From Spec'):
                spec.path(view=app.view_functions[view])

    return spec, version


def config_value(option: str, *, config: Config = None) -> str | None:
    """
    Get the value of an option from the config.

    Args:
        option: The option to get the value for.
        config: Optional. Default: flask.current_app.config.

    Returns:
        str: The config value.
        None: The option was not found.
    """
    if config is None:
        config = current_app.config
    try:
        value = config[CONFIG_SECTION][option]
    except KeyError:
        return None

    reference = _parse_reference(value)
    if reference:
        section, option = reference
        value = config[section][option]

    return value


def _parse_reference(value: str) -> tuple[str, str] | bool:
    """
    Parses a string that may contain a reference to another config value.

    Args:
        value: The string to parse.

    Returns:
        bool: False if the string is not a reference.
        tuple: The section and option of the config value the string is referencing.
    """
    match = re.match(r'^\${([a-z]+):([a-z]+)}$', value, flags=re.IGNORECASE)
    if match:
        section, option = match.groups()
        return str(section), str(option)

    return False


def get_docs_filename(version: str = None, *, config: Config = None) -> str:
    """
    Get the name of a docs file for a specific version.

    Args:
        version: Optional. Default: The version set in the config.
        config: Optional. Default: flask.current_app.config.

    Returns:
        The docs filename.
    """
    if version is None:
        version = config_value('version', config=config)
    docs_title = config_value('title', config=config).replace(' ', '_')
    docs_ext = config_value('docs_type', config=config)

    return f'{docs_title}_{version}.{docs_ext}'


def get_docs_filepath(version: str = None, *, config: Config = None) -> str:
    """
    Get the filepath of a docs file for a specific version.

    Args:
        version: Optional. Default: The version set in the config.
        config: Optional. Default: flask.current_app.config.

    Returns:
        The docs filepath.
    """
    docs_filename = get_docs_filename(version, config=config)
    docs_dir = config_value('docs_dir', config=config)

    return os.path.join(docs_dir, docs_filename)
