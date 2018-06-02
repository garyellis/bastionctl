from ec2_patching import __version__
import logging

cli_tag_key = 'aws-patching'
cli_tag_value = 'true'
cli_version = __version__

ami_name = 'ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server*'
