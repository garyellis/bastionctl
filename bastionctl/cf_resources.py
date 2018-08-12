import re
from troposphere import (
  GetAtt,
  Join,
  Ref,
  Tags,
  Template
)

from troposphere.ec2 import (
  Instance,
  NetworkInterfaceProperty,
  SecurityGroup,
  SecurityGroupEgress,
  SecurityGroupIngress,
  Tag
)


def sanitize_resource_name(name):
    """
    Ensure cloudformation resource names are valid
    """
    nonalphanumeric = re.compile(r'[^a-zA-Z0-9]*')
    sanitized_name = nonalphanumeric.sub('', name).lower()
    return sanitized_name


def tags(name):
    """
    Returns a tags resource containing Name tag 
    """
    return Tags({'Name': name})


def ec2_instance(name, ami_id, keyname, instance_type, sg_ids, subnet_id):
    """
    """
    # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-instance.html
    resource_name = '{}EC2Instance'.format(sanitize_resource_name(name))
    return Instance(
      resource_name,
      ImageId=ami_id,
      InstanceType=instance_type,
      KeyName=keyname,
      NetworkInterfaces=[NetworkInterfaceProperty(
        AssociatePublicIpAddress=True,
        DeviceIndex=0,
        GroupSet=sg_ids,
        SubnetId=subnet_id,
      )],
      Tags=tags(name)
    )


def security_group(name, desc, vpc_id):
    """
    Returns a security group
    """
    resource_name = '{}SG'.format(sanitize_resource_name(name))
    return SecurityGroup(
        resource_name,
        GroupDescription=desc,
        VpcId=vpc_id,
        Tags=tags(name)
    )


def security_group_egress(name, desc, ip_protocol, from_port, to_port, group_id, cidr):
    """
    Returns a security group egress rule resource
    """
    resource_name = '{}SGEgress'.format(sanitize_resource_name(name))
    return SecurityGroupEgress(
        resource_name,
        Description=desc,
        IpProtocol=ip_protocol,
        FromPort=from_port,
        ToPort=to_port,
        GroupId=group_id,
        CidrIp=cidr,
    )


def security_group_ingress(name, desc, ip_protocol, from_port, to_port, group_id, cidr):
    """
    Returns a security group ingress rule resource
    """
    resource_name = '{}SGIngress'.format(sanitize_resource_name(name))
    return SecurityGroupIngress(
        resource_name,
        Description=desc,
        IpProtocol=ip_protocol,
        FromPort=from_port,
        ToPort=to_port,
        GroupId=group_id,
        CidrIp=cidr,
    )


def add_template_resources(template, resources=[]):
    """
    adds a list of resources to the template
    """
    for i in resources:
        template.add_resource(i)


def add_template_outputs(template, outputs=[]):
    """
    """
    for i in outputs:
        template.add_output(i)
