import io
import json

import pytest
import yaml

from awxkit.api.pages import Page
from awxkit.api.pages.users import Users
from awxkit.cli import CLI
from awxkit.cli.format import format_response, strtobool
from awxkit.cli.resource import Import


@pytest.mark.parametrize('truthy', ['y', 'yes', 't', 'true', 'on', '1', 'True', 'YES'])
def test_strtobool_truthy(truthy):
    assert strtobool(truthy) == 1


@pytest.mark.parametrize('falsy', ['n', 'no', 'f', 'false', 'off', '0', 'False', 'NO'])
def test_strtobool_falsy(falsy):
    assert strtobool(falsy) == 0


def test_strtobool_rejects_anything_else():
    with pytest.raises(ValueError):
        strtobool('not-a-truth-value')


def test_json_empty_list():
    page = Page.from_json({'results': []})
    formatted = format_response(page)
    assert json.loads(formatted) == {'results': []}


def test_yaml_empty_list():
    page = Page.from_json({'results': []})
    formatted = format_response(page, fmt='yaml')
    assert yaml.safe_load(formatted) == {'results': []}


def test_json_list():
    users = {
        'results': [
            {'username': 'betty'},
            {'username': 'tom'},
            {'username': 'anne'},
        ]
    }
    page = Users.from_json(users)
    formatted = format_response(page)
    assert json.loads(formatted) == users


def test_yaml_list():
    users = {
        'results': [
            {'username': 'betty'},
            {'username': 'tom'},
            {'username': 'anne'},
        ]
    }
    page = Users.from_json(users)
    formatted = format_response(page, fmt='yaml')
    assert yaml.safe_load(formatted) == users


def test_yaml_import():
    class MockedV2:
        def import_assets(self, data):
            self._parsed_data = data

    def _dummy_authenticate():
        pass

    yaml_fd = io.StringIO(
        """
        workflow_job_templates:
          - name: Workflow1
        """
    )
    yaml_fd.name = 'file.yaml'
    cli = CLI(stdin=yaml_fd)
    cli.parse_args(['--conf.format', 'yaml'])
    cli.v2 = MockedV2()
    cli.authenticate = _dummy_authenticate

    Import().handle(cli, None)
    assert cli.v2._parsed_data['workflow_job_templates'][0]['name']
