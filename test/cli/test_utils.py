import pytest

from awxkit.cli.utils import HelpfulArgumentParser


def make_parser():
    parser = HelpfulArgumentParser(prog='awx')
    parser.add_argument('--conf.host', dest='host')
    return parser


def test_parse_args_succeeds():
    # On Python >= 3.13 argparse calls _parse_known_args() with an extra
    # `intermixed` argument; an incompatible override breaks every parse
    # (https://github.com/ansible/awx/issues/16441)
    parsed = make_parser().parse_args(['--conf.host', 'https://example.org'])
    assert parsed.host == 'https://example.org'


def test_parse_known_args_succeeds():
    parsed, extra = make_parser().parse_known_args(['--conf.host', 'https://example.org', 'jobs', 'list'])
    assert parsed.host == 'https://example.org'
    assert extra == ['jobs', 'list']


def test_parse_intermixed_args_succeeds():
    parsed = make_parser().parse_intermixed_args(['--conf.host', 'https://example.org'])
    assert parsed.host == 'https://example.org'


@pytest.mark.parametrize('help_flag', ['-h', '--help'])
def test_help_flags_are_stripped_instead_of_exiting(help_flag):
    # HelpfulArgumentParser deliberately discards -h/--help so the CLI can
    # print contextual usage info itself rather than argparse exiting early
    parsed = make_parser().parse_args(['--conf.host', 'https://example.org', help_flag])
    assert parsed.host == 'https://example.org'


def test_cli_version_is_resolvable_without_pkg_resources():
    # Must work on a modern venv where setuptools (pkg_resources) is not
    # installed; Python >= 3.13 environments no longer provide it by default
    from awxkit.cli.client import __version__

    assert __version__
