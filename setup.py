#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='sadpanda-downloader',
    version='0.1',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=['src/bin/sadpanda'],

    author='Allen Li',
    author_email='darkfeline@abagofapples.com',
    description='Sadpanda downloader script',
    license='',
    url='',
)
