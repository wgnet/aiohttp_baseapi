#!/usr/bin/env python

import os

from setuptools import setup, find_packages


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(ROOT_DIR, 'VERSION')
BUILD_NUMBER = os.environ.get('BUILD_NUMBER')


def read_file(file_path):
    return open(file_path).read().strip()


__version__ = read_file(os.path.join(ROOT_DIR, 'VERSION'))


if BUILD_NUMBER:
    full_version = '%s.%s' % (__version__, BUILD_NUMBER)
    f = open(VERSION_FILE, 'w')
    try:
        f.writelines([full_version])
    finally:
        f.close()


setup(
    name='aiohttp_baseapi',
    version=read_file(os.path.join(ROOT_DIR, 'VERSION')),
    packages=find_packages(),
    long_description=read_file(os.path.join(ROOT_DIR, 'README.md')),
    include_package_data=True,
    author='Wargaming Team',
    install_requires=[
        'aiohttp>=2.0.0',
        'simplejson>=3.0.0',
    ],
    extras_require={
        'models': [
            'aiosqlalchemy_miniorm'
        ],
    },
    entry_points={'console_scripts': [
        'baseapi-start-project = aiohttp_baseapi.project:execute_from_command_line',
    ]},
    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
