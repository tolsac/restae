#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import restae

setup(
    name='restae',
    version=restae.__version__,
    packages=find_packages(),
    author="Camille TOLSA",
    author_email="camille.tolsa@gmail.com",
    description="REST Framwork for webapp2 & datastore applications",
    long_description=open('README.md').read(),
    url='http://github.com/tolsac/gae-rest-framework',
    include_package_data=True,
    install_requires=[],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    zip_safe=False,
    licence='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]

)