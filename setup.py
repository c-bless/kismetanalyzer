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
    version='0.1.0',
    author='Christoph Bless',
    author_email='bitbucket@cbless.de',
    url='',
    license=' GPLv3',
    description=('TODO'),
    long_description=long_description,
    packages=['kismetanalyzer'],
    install_requires=[
        'argparse',
        'simplekml'
    ],
    entry_points = {
        "console_scripts": [
            "kismet_analyzer_aplist = kismetanalyzer.aplist:gen_aplist"
        ]
    }
)
