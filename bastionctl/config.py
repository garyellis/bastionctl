from bastionctl import __version__
import logging

ami_name = 'ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server*'

cli_tag_key = 'bastionctl'
cli_tag_value = 'true'
cli_version = __version__

stack_output_instance_id_key = 'bastionInstanceId'
stack_output_private_ip_key = 'bastionPrivateIp'
stack_output_public_ip_key = 'bastionPublicIp'
stack_output_vpc_id_key = 'bastionVpcId'

opts = {}
