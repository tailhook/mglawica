#!/usr/bin/env python3

from setuptools import setup

setup(name='barnard',
      version='0.1',
      description='A tool to deploy containers to mglawica cluster',
      author='Paul Colomiets',
      author_email='paul@colomiets.name',
      url='http://github.com/tailhook/mglawica',
      packages=['barnard'],
      install_requires=[
        'PyYaml',
        'trafaret',
        'trafaret_config',
        'vagga2lithos',
        'click',
      ],
      entry_points={
          'console_scripts': [
              'barnard = barnard.main:main',
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
      ],
)
