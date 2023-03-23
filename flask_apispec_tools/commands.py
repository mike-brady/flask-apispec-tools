import json
import sys
from typing import NoReturn

import click
from flask.cli import with_appcontext

from flask_apispec_tools.tools import get_api_spec, get_docs_filename, get_docs_filepath, config_value


@click.command('generate-api-docs')
@click.option('-a', '--all', 'get_everything', flag_value=True, help="Include endpoints marked 'Exclude From Spec'.")
@with_appcontext
def generate_api_docs(get_everything) -> NoReturn:

    spec, version = get_api_spec(
        plugins=config_value('plugins'),
        get_everything=get_everything
    )

    filename = get_docs_filename(version)
    filepath = get_docs_filepath(version)

    def write_file(*, overwrite: bool = False) -> NoReturn:
        mode = 'w' if overwrite else 'x'

        docs_type = config_value('docs_type')
        if docs_type not in ('json', 'yaml'):
            sys.exit("invalid config. docs_type must be either 'json' or 'yaml'")

        with open(filepath, mode) as file:
            file.write(json.dumps(spec.to_dict()))
        print(f'{filename} created.')

    def ask_yn_bool(question: str) -> bool:
        answer = None
        while answer not in ('y', 'n'):
            answer = input(f'{question} (y/n) ')

        return answer == 'y'

    try:
        write_file()
    except FileExistsError:
        print(f'ERROR: {filename} already exists.')
        confirmed = ask_yn_bool(f'Do you want to overwrite {filename}?')
        if confirmed:
            sure = ask_yn_bool(f'Are you sure you want to overwrite {filename}?')
            if sure:
                write_file(overwrite=True)
                return

        sys.exit('aborted')
