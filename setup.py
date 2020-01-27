#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os

readme = open("README.md", "r").read()

history = open("HISTORY.md").read()

requirements = ["jsonschema>=3.2.0", "strict_rfc3339>=0.7", "werkzeug>=0.16.1"]

test_requirements = ["PyYAML", "pytest", "mock", "pytest-readme>=1.0.0",] + requirements

extras = {"test": test_requirements}

metadata = {}
version_filename = os.path.join(
    os.path.dirname(__file__), "lambdarest", "__version__.py"
)
exec(open(version_filename).read(), None, metadata)

setup(
    name="lambdarest",
    version=metadata["__version__"],
    description="pico framework for aws lambda with optional json schema validation",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    author=metadata["__author__"],
    author_email=metadata["__email__"],
    url="https://github.com/trustpilot/python-lambdarest",
    packages=["lambdarest",],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords="lambda aws rest json schema jsonschema",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    test_suite="tests",
    tests_require=test_requirements,
    extras_require=extras,
)
