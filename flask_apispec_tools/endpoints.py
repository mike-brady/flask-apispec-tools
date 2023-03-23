import json
import os
from importlib.resources import files

from flask import render_template_string, jsonify, current_app, request
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from flask_apispec_tools.tools import config_value, get_docs_filepath


class BaseDocs(MethodView):
    def raise_not_found(self, version):
        raise NotFound(f'Docs not found for version {version}')


class Docs(BaseDocs):
    """Exclude From Spec"""
    def get(self):
        """
        ---
        description: Render API documentation as HTML.
        parameters:
            version:
                in: query
        responses:
            200:
                content:
                    text/html: {}
        """
        version = request.args.get('version', config_value('version'))

        docs_title = config_value('title')
        filepath = get_docs_filepath(version)

        if not os.path.isfile(filepath):
            self.raise_not_found(version)

        template_string = files('flask_apispec_tools.templates').joinpath('swagger-ui.html').read_text()

        return render_template_string(
            template_string,
            title=f'{docs_title} {version}',
            docs_json_url=current_app.url_for('flask_apispec_tools_docs_json')
        )


class DocsJSON(BaseDocs):
    """Exclude From Spec"""
    def get(self):
        """
        ---
        description: Get API documentation.
        parameters:
            version:
                in: query
        responses:
            200:
                content:
                    application/json:
                        example:
                            info:
                                description: description
                                title: title
                                version: 1.0.0
                            openapi: 3.0.3
                            paths:
                                /:
                                    get: {}
        """
        version = request.args.get('version', config_value('version'))

        filepath = get_docs_filepath(version)

        try:
            with open(filepath, 'r') as file:
                contents = json.loads(file.read())
        except FileNotFoundError:
            self.raise_not_found(version)

        return jsonify(contents)


class Version(MethodView):
    def get(self):
        """
        ---
        description: Get the version of the API that is currently running.
        responses:
            200:
                content:
                    application/json:
                        example:
                            version: 1.0.0
        """
        return jsonify({'version': config_value('version')})
