import os

import pytest
from flask import Flask

from flask_apispec_tools import endpoints
from flask_apispec_tools.commands import generate_api_docs


def mock_app():
    app = Flask(__name__)

    app.testing = True

    app.config.update({
        'FLASK_APISPEC_TOOLS': {
            'version': '1.2.3',
            'title': 'Some Title',
            'description': 'Some description.',
            'docs_dir': 'tests/test_files/docs/',
            'docs_type': 'json'
        },
        'ANOTHER_SECTION': {
            'option': 'foobar'
        }
    })

    app.cli.add_command(generate_api_docs)

    app.add_url_rule('/docs', view_func=endpoints.Docs.as_view('flask_apispec_tools_docs'), methods=['GET'])
    app.add_url_rule('/docs/json', view_func=endpoints.DocsJSON.as_view('flask_apispec_tools_docs_json'),
                     methods=['GET'])
    app.add_url_rule('/version', view_func=endpoints.Version.as_view('flask_apispec_tools_version'), methods=['GET'])

    return app


@pytest.fixture(scope='session')
def client():
    app = mock_app()

    with app.app_context():
        with app.test_client() as client:
            yield client


@pytest.fixture(scope='session')
def runner():
    app = mock_app()

    # used so that generated docs do not overwrite test files and can be deleted after tests
    app.config['FLASK_APISPEC_TOOLS']['title'] = 'CLI Test'

    return app.test_cli_runner()
