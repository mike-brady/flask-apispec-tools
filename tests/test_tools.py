from unittest.mock import Mock, call

import pytest

from flask_apispec_tools import tools
from tests.setup import client

TEST_MODULE = 'flask_apispec_tools.tools'


@pytest.mark.parametrize('use_client, kwargs', [
    pytest.param(
        False, {},
        id='use-current_client',
    ),
    pytest.param(
        True, {},
        id='client'
    ),
    pytest.param(
        True, {
            'plugins': [0, 1, 2]
        },
        id='plugins'
    ),
    pytest.param(
        True, {
            'get_everything': True
        },
        id='get_everything'
    ),
    pytest.param(
        True, {
            'openapi_version': '9.9.9'
        }
    )
])
def test_get_api_spec(monkeypatch, client, use_client, kwargs):
    mock_apispec_class = Mock('APISpec')
    mock_flask_plugin_class = Mock('FlaskPlugin')
    monkeypatch.setattr(TEST_MODULE + '.APISpec', mock_apispec_class)
    monkeypatch.setattr(TEST_MODULE + '.FlaskPlugin', mock_flask_plugin_class)

    args = []
    if use_client:
        args.append(client.application)

    assert tools.get_api_spec(*args, **kwargs) == (mock_apispec_class.return_value, '1.2.3')

    mock_apispec_class.assert_called_once_with(
        title='Some Title',
        version='1.2.3',
        openapi_version=kwargs.get('openapi_version', '3.0.3'),
        info={
            'description': 'Some description.'
        },
        plugins=[mock_flask_plugin_class.return_value] + kwargs.get('plugins', [])
    )

    mock_path = mock_apispec_class.return_value.path
    if kwargs.get('get_everything', False):
        mock_path.assert_has_calls(
            [
                call(view=client.application.view_functions['flask_apispec_tools_version']),
                call(view=client.application.view_functions['flask_apispec_tools_docs']),
                call(view=client.application.view_functions['flask_apispec_tools_docs_json'])
            ],
            any_order=True
        )
        assert mock_path.call_count == 3
    else:
        mock_path.assert_called_once_with(
            view=client.application.view_functions['flask_apispec_tools_version']
        )


@pytest.mark.parametrize('option, mock_parse_return, use_client, expected', [
    pytest.param(
        'version',
        False,
        True,
        '1.2.3',
        id='version'
    ),
    pytest.param(
        'version',
        ('ANOTHER_SECTION', 'option'),
        True,
        'foobar',
        id='by-reference'
    ),
    pytest.param(
        'not-an-option',
        False,
        True,
        None,
        id='option-does-not-exist'
    ),
    pytest.param(
        'version',
        False,
        False,
        '1.2.3',
        id='use-current_client'
    )
])
def test_config_value(monkeypatch, client, option, mock_parse_return, use_client, expected):
    monkeypatch.setattr(f'{TEST_MODULE}._parse_reference', Mock(return_value=mock_parse_return))
    kwargs = {}
    if use_client:
        kwargs['config'] = client.application.config

    assert tools.config_value(option, **kwargs) == expected


@pytest.mark.parametrize('value, expected', [
    pytest.param(
        'foobar',
        False,
        id='not-a-reference'
    ),
    pytest.param(
        '${foo:bar}',
        ('foo', 'bar'),
        id='is-a-reference'
    )
])
def test_parse_reference(value, expected):
    assert tools._parse_reference(value) == expected


@pytest.mark.parametrize('version, use_client, expected', [
    pytest.param(
        None,
        False,
        'Some_Title_1.2.3.json',
        id='no-args'
    ),
    pytest.param(
        '4.5.6',
        True,
        'Some_Title_4.5.6.json',
        id='with-args'
    )
])
def test_get_docs_filename(client, version, use_client, expected):
    kwargs = {}
    if use_client:
        kwargs['config'] = client.application.config
    assert tools.get_docs_filename(version, **kwargs) == expected


@pytest.mark.parametrize('version, use_client, expected', [
    pytest.param(
        None,
        False,
        'tests/test_files/docs/Some_Title_1.2.3.json',
        id='no-args'
    ),
    pytest.param(
        '4.5.6',
        True,
        'tests/test_files/docs/Some_Title_4.5.6.json',
        id='with-args'
    )
])
def test_get_docs_filepath(client, version, use_client, expected):
    kwargs = {}
    if use_client:
        kwargs['config'] = client.application.config
    assert tools.get_docs_filepath(version, **kwargs) == expected
