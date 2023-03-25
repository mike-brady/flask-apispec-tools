import os

import pytest
from flask import Flask, request, Response
from flask.views import MethodView

from flask_apispec_tools import endpoints
from flask_apispec_tools.commands import generate_api_docs
from flask_apispec_tools.testing import response_validator


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

    app.add_url_rule('/test_endpoint', view_func=TestEndpoint.as_view('test_endpoint'), methods=['GET', 'POST', 'DELETE'])

    app.after_request(response_validator())

    @app.errorhandler(404)
    def not_found(e):
        """Catches 404 responses and returns them without any content. This is specifically for the built-in endpoints
        /docs and /docs/json whose API spec would fail validation due to them not documenting a content type for 404
        responses. This is because they do not directly make a response, but raise a NotFound exception for a Flask app
        to handle. This way the app can choose how to format the 404 response."""
        return Response('', mimetype='text/plain', status=404)

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


class TestEndpoint(MethodView):
    def make_response(self):
        return_status = request.args['return_status']
        return_mime_type = request.args['return_mime_type']
        return_content = request.args['return_content']
        return Response(return_content, status=return_status, mimetype=return_mime_type)

    def get(self):
        """
        ---
        description: Test Endpoint.
        parameters:
            return_status:
                in: query
        responses:
            200:
                content:
                    text/plain: {}
            204:
            400: {}
        """
        return self.make_response()

    def post(self):
        """
        ---
        description: Test Endpoint.
        parameters:
            return_status:
                in: query
        """
        return self.make_response()

    def delete(self):
        return self.make_response()

    def put(self):
        return self.make_response()
