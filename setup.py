#!/usr/bin/env python
"""
Build script for fonts-tweak-tool
"""
from setuptools import setup, find_packages

setup (name = "fonts-tweak-tool",
    version = "0.0.2",
    packages = find_packages(),
    install_requires=[
        'libeasyfc'
    ],
    description = "Fonts Tweak Tool.",
    author = 'Jian Ni',
    author_email = 'jni@redhat.com',
    license = 'LGPLv3+',
    platforms=["Linux"],
    scripts = ["fonts-tweak-tool"],

    package_data = {'fontstweak':['fontstools.ui', 'locale-list']},   
    include_package_data = True, 
    classifiers=['License :: OSI Approved ::  GNU Lesser General Public License (LGPL)',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 ]
)
