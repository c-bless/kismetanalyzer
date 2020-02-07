# -*- coding: utf-8 -*-
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='kismet-analyzer',
    version='0.3.1',
    author='Christoph Bless',
    author_email='bitbucket@cbless.de',
    url='https://bitbucket.org/cbless/kismetanalyzer',
    license=' GPLv3',
    description=('Library for parsing kismet results from the .kismet database file.'),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['kismetanalyzer'],
    install_requires=[
        'fastkml',
        'pygeoif',
        'lxml'
    ],
    entry_points = {
        "console_scripts": [
            "kismet_analyzer_aplist = kismetanalyzer.aplist:gen_aplist",
            "kismet_analyzer_clientlist = kismetanalyzer.clientlist:gen_clientlist",
        ]
    }
)
