import typing

from apispec.exceptions import APISpecError
from flask import Response, request, current_app

from flask_apispec_tools.tools import get_api_spec


def response_validator() -> typing.Callable[[Response], Response]:
    def validate_response(response: Response) -> Response:
        # Validation Check 1
        # If there is no endpoint for the requested path, there is nothing to validate
        # Validation Check 2
        # If a request was made with an unallowed method, there is nothing to validate
        if request.endpoint is None:
            return response

        status_code = str(response.status_code)

        if '_test_spec' not in current_app.config['FLASK_APISPEC_TOOLS']:
            spec, _ = get_api_spec(current_app, get_everything=True)
            current_app.config['FLASK_APISPEC_TOOLS']['_test_spec'] = spec
        else:
            spec = current_app.config['FLASK_APISPEC_TOOLS']['_test_spec']

        path = request.path
        endpoint_spec = spec._paths[path]
        method = request.method.lower()

        try:
            # Validation Check 3
            # Is it possible to be in this state? apispec will always include the method in the spec
            # even if there is no docstring at all, as long as the endpoint and method are registered Flask
            assert method in endpoint_spec, f'{method} missing'
            endpoint_spec = endpoint_spec[method]

            # Validation Check 4
            assert 'responses' in endpoint_spec, 'responses missing'
            endpoint_spec = endpoint_spec['responses']

            # Validation Check 5
            assert status_code in endpoint_spec, f'{status_code} missing'
            endpoint_spec = endpoint_spec[status_code]

            # Validation Check 6
            if 'content' not in endpoint_spec and response.content_length == 0:
                return response

            # Validation Check 7
            assert 'content' in endpoint_spec, f'content missing'
            endpoint_spec = endpoint_spec['content']

            # Validation Check 8
            mime_type = response.mimetype
            assert mime_type in endpoint_spec, f'{mime_type} missing'
        except AssertionError as e:
            raise APISpecError(f'{method.upper()} {path} -> {status_code}: {str(e)}')

        return response
    return validate_response
