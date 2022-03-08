
from setuptools import setup, find_packages
from sp_api_cli.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='sp_api_cli',
    version=VERSION,
    description='Command line interface for Amazons Selling-Partner API.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Michael Primke',
    author_email='info@saleweaver.com',
    url='https://github.com/saleweaver/sp_api_cli',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'sp_api_cli': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        sp-api = sp_api_cli.main:main
    """,
)
