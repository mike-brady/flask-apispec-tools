from contextlib import nullcontext as does_not_raise

import pytest
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask
from werkzeug.routing import BuildError

import flask_apispec_tools


@pytest.mark.parametrize('initial_config, kwargs, raises, error_message', [
    pytest.param(
        {},
        {},
        does_not_raise(), None,
        id='no-kwargs'
    ),
    pytest.param(
        None,
        {},
        pytest.raises(ValueError), "[flask-apispec-tools] invalid config. docs_type must be either 'json' or 'yaml'",
        id='invalid-config'
    ),
    pytest.param(
        {},
        {
            'docs_endpoint': '/foobar',
            'docs_json_endpoint': '/foobar2',
            'version_endpoint': '/foobar3'
        },
        does_not_raise(), None,
        id='custom-endpoints'
    ),
    pytest.param(
        {},
        {
            'docs_endpoint': False,
            'docs_json_endpoint': False,
            'version_endpoint': False
        },
        does_not_raise(), None,
        id='disable-endpoints'
    ),
    pytest.param(
        {},
        {
            'docs_endpoint': '/foobar',
            'docs_json_endpoint': False,
            'version_endpoint': '/foobar3'
        },
        pytest.raises(ValueError), 'docs_json_endpoint can not be False when docs_endpoint is not False',
        id='disable-only-docs_json'
    ),
    pytest.param(
        {
            'FLASK_APISPEC_TOOLS': {'docs_type': 'json'}
        },
        {'config_values': {'docs_type': 'yaml'}},
        does_not_raise(), None,
        id='config_values'
    ),
    pytest.param(
        {},
        {'plugins': [FlaskPlugin()]},
        does_not_raise(), None,
        id='plugins'
    )
])
def test_init(initial_config, kwargs, raises, error_message):
    app = Flask(__name__)
    if initial_config:
        app.config.update(initial_config)
    elif initial_config is not None:
        app.config['FLASK_APISPEC_TOOLS'] = {
            'docs_type': 'json'
        }
    with raises as e:
        flask_apispec_tools.init(app, **kwargs)

    if error_message:
        assert str(e.value) == error_message
    else:
        with app.test_request_context():
            expected_docs_endpoint = kwargs.get('docs_endpoint', '/docs')
            with does_not_raise() if expected_docs_endpoint else pytest.raises(BuildError):
                assert app.url_for('flask_apispec_tools_docs') == expected_docs_endpoint

            expected_docs_json_endpoint = kwargs.get('docs_json_endpoint', '/docs/json')
            with does_not_raise() if expected_docs_json_endpoint else pytest.raises(BuildError):
                assert app.url_for('flask_apispec_tools_docs_json') == expected_docs_json_endpoint

            expected_version_endpoint = kwargs.get('version_endpoint', '/version')
            with does_not_raise() if expected_version_endpoint else pytest.raises(BuildError):
                assert app.url_for('flask_apispec_tools_version') == expected_version_endpoint

        if 'config_values' in kwargs:
            for key, value in kwargs['config_values'].items():
                assert app.config['FLASK_APISPEC_TOOLS'][key] == value

        if 'plugins' in kwargs:
            assert 'plugins' in app.config['FLASK_APISPEC_TOOLS']
            assert app.config['FLASK_APISPEC_TOOLS']['plugins'] == kwargs['plugins']
