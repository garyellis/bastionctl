from troposphere import Template
from troposphere import GetAtt
from troposphere import Ref
from aws_patching import cf_resources

# this can be genericised and placed into cf_resources module
def sg_ingress_allow_bastion_ip(bastion_ip, sg_ids):
    """
    Troposphere sg ingress rules helper
    """
    rules = []
    for i, sg_id in enumerate(sg_ids):
        rules.append(
            cf_resources.security_group_ingress(
                name='AllowBastion{}'.format(i),
                desc='Allow bastion (linux patching)',
                ip_protocol='tcp',
                from_port=22,
                to_port=22,
                group_id=sg_id,
                cidr=bastion_ip
            )
        )
    return rules

def create_bastion_template(name, ami_id, instance_type, subnet_id, vpc_id, bastion_sg_ingress, sg_ids):
    """
    Returns the  bastion cloudformation template
    """
    pass

    t = Template()
    t.add_description('Rendered by python troposphere')

    # setup our bastion security group and ec2 instance
    bastion_sg = cf_resources.security_group(
      name=name,
      desc=name,
      vpc_id=vpc_id
    )

    bastion_sg_ingress = cf_resources.security_group_ingress(
      name=name,
      desc=name,
      ip_protocol='tcp',
      from_port=22,
      to_port=22,
      group_id=Ref(bastion_sg),
      cidr=bastion_sg_ingress
    )

    bastion_sg_egress_tcp_name = '{}-tcp-all'.format(name)
    bastion_sg_egress_tcp = cf_resources.security_group_egress(
      name=bastion_sg_egress_tcp_name,
      desc=bastion_sg_egress_tcp_name,
      ip_protocol='tcp',
      from_port='-1',
      to_port='-1',
      group_id=Ref(bastion_sg),
      cidr='0.0.0.0/0'
    )

    bastion_sg_egress_udp_name = '{}-udp-all'.format(name)
    bastion_sg_egress_udp = cf_resources.security_group_egress(
      name=bastion_sg_egress_udp_name,
      desc=bastion_sg_egress_udp_name,
      ip_protocol='udp',
      from_port='-1',
      to_port='-1',
      group_id=Ref(bastion_sg),
      cidr='0.0.0.0/0'
    )   

    bastion_instance = cf_resources.ec2_instance(
      name=name,
      ami_id=ami_id,
      keyname='',
      instance_type=instance_type,
      sg_ids=[Ref(bastion_sg)],
      subnet_id=subnet_id
    )

    # allow sg ingress on to the bastion ip
    sg_ingress_bastion_ip = sg_ingress_allow_bastion_ip(
        bastion_ip=GetAtt(bastion_instance, 'PrivateIp'),
        sg_ids=sg_ids
    )


    cf_resources.add_template_resources(
        template=t,
        resources=[
            bastion_sg,
            bastion_sg_ingress,
            bastion_sg_egress_tcp,
            bastion_sg_egress_udp,
            bastion_instance,
            sg_ingress_bastion_ip
        ]
    )

    return t.to_yaml()
