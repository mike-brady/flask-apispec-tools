import json
import os
import shutil

import pytest

from tests.setup import runner

TEST_MODULE = 'flask_apispec_tools.tools'

docs_filename = 'CLI_Test_1.2.3.json'


@pytest.fixture(scope='function')
def remove_generated_docs(runner):
    yield

    docs_dir = runner.app.config['FLASK_APISPEC_TOOLS']['docs_dir']
    if os.path.isfile(os.path.join(docs_dir, 'CLI_Test_1.2.3.json')):
        os.remove(os.path.join(docs_dir, docs_filename))


@pytest.mark.usefixtures('remove_generated_docs')
@pytest.mark.parametrize('args, inputs, make_existing_file, succeeds', [
    pytest.param(
        [], [],
        False, True,
        id='no-args-no-existing-file'
    ),
    pytest.param(
        ['-a'], [],
        False, True,
        id='-a-no-existing-file'
    ),
    pytest.param(
        ['--all'], [],
        False, True,
        id='-all-no-existing-file'
    ),
    pytest.param(
        [], ['y', 'y'],
        True, True,
        id='existing-file-y-y'
    ),
    pytest.param(
        [], ['y', 'n'],
        True, False,
        id='existing-file-y-n'
    ),
    pytest.param(
        [], ['n'],
        True, False,
        id='existing-file-n'
    ),
    pytest.param(
        [], ['x', 'b', 'y', 'n'],
        True, False,
        id='existing-file-x-b-y-n'
    ),
    pytest.param(
        [], ['x', 'b', 'y', 'y'],
        True, True,
        id='existing-file-x-b-y-y'
    ),
    pytest.param(
        [], ['y', 'x', 'b', 'n'],
        True, False,
        id='existing-file-y-x-b-n'
    ),
    pytest.param(
        [], ['y', 'x', 'b', 'y'],
        True, True,
        id='existing-file-y-x-b-n'
    ),
    pytest.param(
        ['--help'], [],
        False, False,
        id='--help'
    )
])
def test_generate_api_docs(runner, args, inputs, make_existing_file, succeeds):
    docs_dir = runner.app.config['FLASK_APISPEC_TOOLS']['docs_dir']
    docs_filepath = os.path.join(docs_dir, docs_filename)
    if make_existing_file:
        shutil.copy(os.path.join(docs_dir, 'Some_Title_1.2.3.json'), docs_filepath)

    input_str = '\n'.join(inputs)

    result = runner.invoke(args=['generate-api-docs', *args], input=input_str)

    expected = ''
    success_msg = f'{docs_filename} created.'
    aborted_msg = 'aborted'
    if make_existing_file:
        expected += f'ERROR: {docs_filename} already exists.{os.linesep}'
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
    elif '--help' in args:
        expected += 'Usage: tests.setup generate-api-docs [OPTIONS]\n\n'
        expected += 'Options:\n'
        expected += '  -a, --all  Include endpoints marked \'Exclude From Spec\'.\n'
        expected += '  --help     Show this message and exit.'

    expected += os.linesep

    assert result.output == expected

    if succeeds or make_existing_file:
        assert os.path.isfile(docs_filepath)

        with open(docs_filepath, 'r') as file:
            contents = json.loads(file.read())

        if succeeds:
            assert contents.get('info') == {"description": "Some description.", "title": "CLI Test", "version": "1.2.3"}
            assert contents.get('openapi') == "3.0.3"
            paths = contents.get('paths', {})
            assert '/version' in paths
            if '-a' in args or '--all' in args:
                assert '/docs' in paths
                assert '/docs/json' in paths
            else:
                assert '/docs' not in paths
                assert '/docs/json' not in paths

        else:
            assert contents == {'these': 'are', 'some': 'docs'}

        os.remove(docs_filepath)
    else:
        assert not os.path.isfile(docs_filepath)
