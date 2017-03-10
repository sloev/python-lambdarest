#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()


readme = read_md('README.md')

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'jsonschema>=2.5.1',
    'strict_rfc3339>=0.7',
]

test_requirements = [
    'mock',
]

setup(
    name='lambdarest',
    version='2.2.0',
    description="pico framework for aws lambda with optional json schema validation",
    long_description=readme + '\n\n' + history,
    author="jgv",
    author_email='jgv@trustpilot.com',
    url='https://github.com/trustpilot/python-lambdarest',
    packages=[
        'lambdarest',
    ],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='lambda aws rest json schema jsonschema',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
