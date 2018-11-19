#!/usr/bin/env python
# coding=utf-8

"""
python distribute file
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from setuptools import setup, find_packages


def requirements_file_to_list(fn="requirements.txt"):
    """read a requirements file and create a list that can be used in setup.

    """
    with open(fn, 'r') as f:
        return [x.rstrip() for x in list(f) if x and not x.startswith('#')]


setup(
    name="pihmatch",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements_file_to_list(),
    dependency_links=[
        # If your project has dependencies on some internal packages that is
        # not on PyPI, you may list package index url here. Then you can just
        # mention package name and version in requirements.txt file.
    ],
    entry_points={
        # 'console_scripts': [
        #     'main = mypkg.main:main',
        # ]
    },
    package_data={
        # 'mypkg': ['logger.conf']
    },
    author="Robin Herrmann",
    author_email="robin.herrmann@tu-dresden.de",
    description="A suite for testing Perceptual Image Hashing algorithms that should be used for content identification.",
    long_description=open('README.md').read(),
    license="GPLv2+",
    url="",
)
