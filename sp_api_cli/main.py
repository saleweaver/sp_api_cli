
from cement import App, TestApp, init_defaults
from cement.core.exc import CaughtSignal
from cement.ext.ext_argparse import ArgparseArgumentHandler

from .core.exc import SpApiError
from .controllers.base import Base, SpReports

# configuration defaults
CONFIG = init_defaults('sp_api')
CONFIG['sp_api']['foo'] = 'bar'


class ModifiedArgparseArgumentHandler(ArgparseArgumentHandler):
    class Meta:
        label = 'modified_argparse'
        ignore_unknown_arguments = True

    def __init__(self, *args, **kw):
        super(ModifiedArgparseArgumentHandler, self).__init__(*args, **kw)


class SpApi(App):
    """SP API CLI primary application."""

    class Meta:
        label = 'sp_api'

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2',
            'json'
        ]

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        # set the output handler
        output_handler = 'json'

        # register handlers
        handlers = [
            ModifiedArgparseArgumentHandler,
            Base,
            SpReports
        ]


class SpApiTest(TestApp,SpApi):
    """A sub-class of SpApi that is better suited for testing."""

    class Meta:
        label = 'sp_api'


def main():
    with SpApi() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except SpApiError as e:
            print('SpApiError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
