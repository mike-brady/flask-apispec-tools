import json
import os
import shutil

import pytest

from tests.setup import runner

TEST_MODULE = 'flask_apispec_tools.tools'

docs_filename = 'CLI_Test_1.2.3.json'


@pytest.mark.parametrize('arg, inputs, make_existing_file, config, succeeds', [
    pytest.param(
        None, [],
        False, None, True,
        id='no-args-no-existing-file'
    ),
    pytest.param(
        '-a', [],
        False, None, True,
        id='-a-no-existing-file'
    ),
    pytest.param(
        '--all', [],
        False, None, True,
        id='-all-no-existing-file'
    ),
    pytest.param(
        None, ['y', 'y'],
        True, None, True,
        id='existing-file-y-y'
    ),
    pytest.param(
        None, ['y', 'n'],
        True, None, False,
        id='existing-file-y-n'
    ),
    pytest.param(
        None, ['n'],
        True, None, False,
        id='existing-file-n'
    ),
    pytest.param(
        None, ['x', 'b', 'y', 'n'],
        True, None, False,
        id='existing-file-x-b-y-n'
    ),
    pytest.param(
        None, ['x', 'b', 'y', 'y'],
        True, None, True,
        id='existing-file-x-b-y-y'
    ),
    pytest.param(
        None, ['y', 'x', 'b', 'n'],
        True, None, False,
        id='existing-file-y-x-b-n'
    ),
    pytest.param(
        None, ['y', 'x', 'b', 'y'],
        True, None, True,
        id='existing-file-y-x-b-n'
    ),
    pytest.param(
        '--help', [],
        False, None, False,
        id='--help'
    ),
    pytest.param(
        None, [],
        False, {'docs_type': 'foobar'}, False,
        id='invalid-config'
    )
])
def test_generate_api_docs(runner, arg, inputs, make_existing_file, config, succeeds):
    docs_dir = runner.app.config['FLASK_APISPEC_TOOLS']['docs_dir']
    if config:
        runner.app.config['FLASK_APISPEC_TOOLS'].update(config)
    docs_filepath = os.path.join(docs_dir, docs_filename)
    if make_existing_file:
        shutil.copy(os.path.join(docs_dir, 'Some_Title_1.2.3.json'), docs_filepath)

    input_str = '\n'.join(inputs)

    args = ['generate-api-docs']
    if arg:
        args.append(arg)
    result = runner.invoke(args=args, input=input_str)

    expected = ''
    success_msg = f'{docs_filename} created.'
    aborted_msg = 'aborted'
    if make_existing_file:
        expected += f'ERROR: {docs_filename} already exists.\n'
        user_input = None
        i = 0
        while user_input not in {'y', 'n'}:
            expected += f'Do you want to overwrite {docs_filename}? (y/n) '
            user_input = inputs[i]
            i += 1
        if user_input == 'y':
            user_input = None
            while user_input not in {'y', 'n'}:
                expected += f'Are you sure you want to overwrite {docs_filename}? (y/n) '
                user_input = inputs[i]
                i += 1
            if user_input == 'y':
                expected += success_msg
            else:
                expected += aborted_msg
        else:
            expected += aborted_msg
    elif succeeds:
        expected += success_msg

    if arg == '--help':
        expected += 'Usage: tests.setup generate-api-docs [OPTIONS]\n\n'
        expected += 'Options:\n'
        expected += '  -a, --all  Include endpoints marked \'Exclude From Spec\'.\n'
        expected += '  --help     Show this message and exit.'

    if config:
        expected += "Invalid config. docs_type must be either 'json' or 'yaml'"

    expected += '\n'

    # get file's existence and contents, so we can delete it before starting assertions
    file_exists = os.path.isfile(docs_filepath)
    if file_exists:
        with open(docs_filepath, 'r') as file:
            contents = json.loads(file.read())
        os.remove(docs_filepath)

    assert result.output == expected

    if succeeds or make_existing_file:
        assert file_exists

        if succeeds:
            assert contents.get('info') == {'description': 'Some description.', 'title': 'CLI Test', 'version': '1.2.3'}
            assert contents.get('openapi') == "3.0.3"
            paths = contents.get('paths', {})
            assert '/version' in paths
            if arg in ('-a',  '--all'):
                assert '/docs' in paths
                assert '/docs/json' in paths
            else:
                assert '/docs' not in paths
                assert '/docs/json' not in paths

        else:
            assert contents == {'these': 'are', 'some': 'docs'}

    else:
        assert not os.path.isfile(docs_filepath)
