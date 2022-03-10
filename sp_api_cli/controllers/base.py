import os
from datetime import datetime, timedelta

from cement import Controller, ex
from cement.utils.shell import Prompt
from cement.utils.version import get_version_banner
from sp_api.base import Marketplaces

from ..core.version import get_version
from sp_api.api import Reports

VERSION_BANNER = """
Command line interface for Amazons Selling-Partner API. %s
%s
""" % (get_version(), get_version_banner())


class Confirm(Prompt):
    class Meta:
        text = "Do you want to continue?"
        options = ['y', 'n']
        options_separator = '|'
        default = 'y'
        clear = False
        max_attempts = 99

    def process_input(self):
        if self.input.lower() == 'y':
            pass
        else:
            # don't do anything... maybe exit?
            exit(1)


class SelectionList(Prompt):
    def __init__(self, options, next_token=None, app=None, *args, **kw):
        self.Meta.options = options
        self.next_token = next_token
        self.app = app
        super().__init__(*args, **kw)


    class Meta:
        text = 'Select a report'
        numbered = True
        max_attempts = 99
        clear = True

    def process_input(self):
        if self.input == 'Next Page':
            r = get_client(Reports, self.app).get_reports(nextToken=self.next_token)
            report_pages = [
                f"{r['reportId']} --- {r['processingStatus']} --- {r['dataStartTime']} --- {r['dataEndTime']}" for r in
                r.reports]
            if r.next_token:
                report_pages = report_pages + ['Next Page']
            SelectionList(report_pages, r.next_token, self.app)
        else:
            print('hier')

class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'Command line interface for Amazon\'s Selling-Partner API.'

        # text displayed at the bottom of --help output
        epilog = 'Usage: sp-api'
        # controller level arguments. ex: 'sp_api --version'
        arguments = [
            ### add a version banner
            (['-v', '--version'],
             {'action': 'version',
              'version': VERSION_BANNER}),
            (['-a', '--account', '--acc'], {
                'help': 'Set the account to use, defaults to default',
                'action': 'store',
                'dest': 'account',
                'default': 'default'
            }),
            (['-m', '--marketplace', '--mp'], {
                'help': 'Set the marketplace to use, defaults to US',
                'action': 'store',
                'dest': 'marketplace',
                'default': 'US'
            }),
            (['-r', '--refresh_token', '--rt'], {
                'help': 'Set the refresh token, overrides default',
                'action': 'store',
                'dest': 'refresh_token'
            })
        ]

    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()


class IllegalRequestException(Exception):
    pass


def get_client(client, app):
    return client(
        refresh_token=app.pargs.refresh_token,
        account=app.pargs.account,
        marketplace=Marketplaces[app.pargs.marketplace or os.environ.get('SP_API_DEFAULT_MARKETPLACE', 'US')]
    )


class SpReports(Controller):
    class Meta:
        label = 'reports'
        description = 'Report Operations'
        epilog = 'Usage: sp-api reports ...'
        stacked_on = 'base'
        stacked_type = 'nested'

    @ex(help='Get Report by ID', arguments=[(['reportId'],
                                             dict(type=str, metavar='REPORT_ID', action='store'))])
    def get(self):
        self.app.render(
            get_client(Reports, self.app)
                .get_report(self.app.pargs.reportId)()
        )

    @ex(help='Create report', arguments=[
        (['reportType'], dict(type=str, metavar='REPORT_TYPE', action='store')),
        (['--timeBack', '--since', '-s'], {'action': 'store', 'dest': 'time_back', 'help': 'Lookback by'}),
        (['--timeBackUnits', '--units', '-u'],
         {'action': 'store', 'dest': 'time_back_units', 'help': 'Lookback units, must be used with time back',
          'default': 'days'}),
        (['--options', '-o'], {'action': 'store', 'dest': 'options', 'help': 'Report Options'}),
    ])
    def create(self):
        opts = {'reportType': self.app.pargs.reportType}
        if self.app.pargs.time_back:
            opts.update({
                'dataStartTime': datetime.utcnow() - timedelta(
                    **{self.app.pargs.time_back_units: self.app.pargs.time_back}),
                'dataEndTime': datetime.utcnow()
            })
        self.app.render(get_client(Reports, self.app).create_report(**opts)())

    @ex(help='List Reports by type', arguments=[
        (['reportTypes'], dict(type=str, metavar='REPORT_TYPES', action='store')),
        (['--processingStatuses', '-p'], dict(dest='processingStatuses', action='store'))
    ])
    def list(self):
        if self.app.pargs.processingStatuses:
            res = get_client(Reports, self.app).get_reports(reportTypes=self.app.pargs.reportTypes.split(','),
                                                            processingStatuses=self.app.pargs.processingStatuses.split(
                                                                ','))
        else:
            res = get_client(Reports, self.app).get_reports(reportTypes=self.app.pargs.reportTypes.split(','))
        report_pages = [f"{r['reportId']} --- {r['processingStatus']} --- {r['dataStartTime']} --- {r['dataEndTime']}" for r in res.reports]
        if res.next_token:
            report_pages = report_pages + ['Next Page']
        SelectionList(report_pages, res.next_token, self.app)



    @ex(
        help='Download Report',
        arguments=[
            (['reportDocumentId'], dict(type=str, metavar='REPORT_DOCUMENT_ID', action='store')),
            (['file'], dict(type=str, metavar='FILE_NAME', action='store')),
        ]
    )
    def download(self):
        if os.path.exists(self.app.pargs.file):
            print('File exists. Override?')
            Confirm()
        self.app.render(get_client(Reports, self.app).get_report_document(self.app.pargs.reportDocumentId,
                                                                          file=open(self.app.pargs.file, 'w+'))())
        self.app.log.info(f'''File saved! {os.path.abspath(self.app.pargs.file)}''')

