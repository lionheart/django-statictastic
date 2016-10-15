#!/usr/bin/env/python3

import os
import runpy

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

metadata = runpy.run_path("statictastic/metadata.py")

setup(
    name='django-statictastic',
    version=metadata['__version__'],
    license=metadata['__license__'],
    description='A fantastic way to sync your files to S3.',
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    packages=[
        'statictastic',
        'statictastic.management',
        'statictastic.management.commands',
        'statictastic.templatetags',
    ],
    install_requires=["requests>=2.0.0", "cssmin>=0.2.0", "lxml>=3.0.0"],
)

