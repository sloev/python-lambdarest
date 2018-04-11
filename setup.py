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
    'werkzeug>=0.14.1'
]

test_requirements = [
    'flake8==2.6.0',
    'coverage==4.1',
    'PyYAML==3.11',
    'pytest==2.9.2',
    'mock>=2.0.0',
    'pytest-readme>=1.0.0',
    'isort==4.2.15', # dependency of pylint
    'prospector>=0.12.5',
    'jsonschema>=2.5.1',
    'strict_rfc3339>=0.7'
] + requirements

extras = {
    'test': test_requirements
}

setup(
    name='lambdarest',
    version='4.1.0',
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
    tests_require=test_requirements,
    extras_require=extras
)
