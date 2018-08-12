from bastionctl import __version__
from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='bastionctl',
    version=__version__,
    description='EC2 patching helpers',
    author='Gary Ellis',
    author_email='gellis@infiniticg.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['bastionctl = bastionctl.cli:cli']
    },
    install_requires=[
      'boto3',
      'click',
      'requests',
      'pycrypto',
      'tabulate',
      'troposphere'
    ]
)
