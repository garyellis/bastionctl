from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='aws_patching',
    version='0.1.0',
    description='AWS patching helpers',
    author='Gary Ellis',
    author_email='gary.luis.ellis@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['ec2-patching = aws_patching.cli:cli']
    },
    install_requires=[
      'boto3',
      'click',
      'pycrypto',
      'troposphere'
    ]
)
