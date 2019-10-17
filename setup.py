#!/usr/bin/env/python3
# -*- coding: utf-8 -*-

# Copyright 2012-2017 Lionheart Software LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
    install_requires=["requests>=2.0.0", "cssmin>=0.2.0", "lxml>=3.0.0", "boto3>=1.9.239", "django-storages>=1.7.1"],
)

