from ec2_patching import __version__
from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='ec2_patching',
    version=__version__,
    description='EC2 patching helpers',
    author='Gary Ellis',
    author_email='gellis@infiniticg.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['ec2-patching = ec2_patching.cli:cli']
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
