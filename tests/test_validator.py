from contextlib import nullcontext as does_not_raise

import pytest
from apispec.exceptions import APISpecError

from tests.setup import client


@pytest.mark.parametrize('method, path, return_status, return_mime_type, return_content, exception, expected', [
    pytest.param(
        'get', '/path-not-found', None, None, None, does_not_raise(), None,
        id='VC1-endpoint-does-not-exist'
    ),
    pytest.param(
        'put', None, None, None, None, does_not_raise(), None,
        id='VC2-method-not-allowed'
    ),
    pytest.param(
        'put', None, None, None, None, pytest.raises(APISpecError), 'put missing',
        id='VC3-no-method',
        marks=pytest.mark.xfail(reason='this condition should be unreachable as apispec always includes the method')
    ),
    pytest.param(
        'post', None, None, None, None, pytest.raises(APISpecError), 'responses missing',
        id='VC4-docstring-without-responses'
    ),
    pytest.param(
        'delete', None, None, None, None, pytest.raises(APISpecError), 'responses missing',
        id='VC4-no-docstring'
    ),
    pytest.param(
        'get', None, 202, None, None, pytest.raises(APISpecError), '202 missing',
        id='VC5-no-status-code'
    ),
    pytest.param(
        'get', None, 400, None, None, pytest.raises(APISpecError), 'content missing',
        id='VC6-no-content-with-response-body'
    ),
    pytest.param(
        'get', None, 204, None, '', does_not_raise(), None,
        id='VC7-no-content-without-response-body'
    ),
    pytest.param(
        'get', None, None, 'text/html', None, pytest.raises(APISpecError), 'text/html missing',
        id='VC8-no-mime-type'
    ),
    pytest.param(
        'get', None, None, None, None, does_not_raise(), None,
        id='VC9-pass'
    ),
])
def test_endpoint(client, method, path, return_status, return_mime_type, return_content, exception, expected):
    if path is None:
        path = '/test_endpoint'
    if return_status is None:
        return_status = 200

    query_string = {
        'return_status': return_status,
        'return_mime_type': return_mime_type or 'text/plain',
        'return_content': return_content if return_content is not None else 'There was a fish in the percolator!'
    }

    with exception as e:
        getattr(client, method)(path, query_string=query_string)

    if expected is not None:
        assert str(e.value) == f'{method.upper()} {path} -> {return_status}: {expected}'
