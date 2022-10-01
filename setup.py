#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
import unittest

# Read the contents of the README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(name='rtspwebviewer',
    version='0.1.2',
    description='Simple web viewer for RTSP streams.',
    author='Luis C. Garcia-Peraza Herrera',
    author_email='luiscarlos.gph@gmail.com',
    license='MIT',
    url='https://github.com/luiscarlosgph/rtspwebviewer',
    packages=['rtspwebviewer'],
    package_dir={'rtspwebviewer' : 'src'}, 
    install_requires=[
        'argparse',
        'opencv-python',
        'imutils',
        'flask',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    zip_safe=False,
)
