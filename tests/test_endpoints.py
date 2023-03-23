import pytest

from tests.setup import client


@pytest.mark.parametrize('params, status_code', [
    pytest.param(
        {}, 200,
        id='no-params'
    ),
    pytest.param(
        {'version': '1.2.3'}, 200,
        id='version-found'
    ),
    pytest.param(
        {'version': '3.2.1'}, 404,
        id='version-not-found'
    ),
    pytest.param(
        {'foobar': 'abcd'}, 200,
        id='extra-param'
    )
])
def test_docs(client, params, status_code):
    response = client.get('/docs', query_string=params)

    assert response.status_code == status_code
    assert response.mimetype == 'text/html'
    if status_code == 200:
        assert '<!-- such a simple thing -->' in response.text
    else:
        assert '<!-- such a simple thing -->' not in response.text


@pytest.mark.parametrize('params, status_code', [
    pytest.param(
        {}, 200,
        id='no-params'
    ),
    pytest.param(
        {'version': '1.2.3'}, 200,
        id='version-found'
    ),
    pytest.param(
        {'version': '3.2.1'}, 404,
        id='version-not-found'
    ),
    pytest.param(
        {'foobar': 'abcd'}, 200,
        id='extra-param'
    )
])
def test_docs_json(client, params, status_code):
    response = client.get('/docs/json', query_string=params)

    assert response.status_code == status_code
    if status_code == 200:
        assert response.mimetype == 'application/json'
        assert response.json == {'these': 'are', 'some': 'docs'}
    else:
        assert response.mimetype == 'text/html'


def test_version(client):
    response = client.get('/version')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json == {'version': '1.2.3'}
