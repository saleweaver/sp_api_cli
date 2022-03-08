from datetime import datetime

from pytest import raises
from sp_api_cli.main import SpApiTest


def test_sp_api():
    # test sp_api without any subcommands or arguments
    with SpApiTest() as app:
        app.run()
        assert app.exit_code == 0


def test_sp_api_debug():
    # test that debug mode is functional
    argv = ['--debug']
    with SpApiTest(argv=argv) as app:
        app.run()
        assert app.debug is True


def test_command1():
    # test command1 without arguments
    argv = ['reports', 'get', '-r', 'rr']
    with SpApiTest(argv=argv) as app:
        app.run()
