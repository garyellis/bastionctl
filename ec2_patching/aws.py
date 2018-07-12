import ec2_patching.config as config
import ec2_patching.keypairs
import boto3
from botocore.exceptions import ClientError
from operator import itemgetter
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

def get_session(profile_name,region_name='us-west-2'):
    """
    Returns a boto session for the given profile and region
    """
    session = boto3.session.Session(profile_name=profile_name, region_name=region_name)
    return session

def get_ec2_regions(session):
    """
    returns a list of available regions for the ec2 service
    """
    return session.get_available_regions('ec2')

def get_default_ami(session):
    """
    Returns the latest Ubuntu Xenial ImageId
    """
    ami_name = config.ami_name
    client = session.client('ec2')
    amis = client.describe_images(Filters=[{ 'Name': 'name', 'Values': [ami_name] }])['Images']
    ami = sorted(amis, key=itemgetter('Name'), reverse=True)[0]
    return ami

def get_ami_name(session, ami_id):
    """
    Returns the ami name for the given image id
    """
    client = session.client('ec2')
    ami_name = ''
    ami = client.describe_images(Filters=[{'Name': 'image-id', 'Values': [ami_id]}])['Images']
    if ami:
        ami_name = ami[0].get('Name')
    return ami_name

def filter_vpc_id(vpc_id):
    """
    vpc filter helper
    """
    return {'Filters': [{'Name': 'vpc-id', 'Values': [vpc_id]}]}

def get_tag_value(tags, key='Name'):
    """
    tags helper
    """
    value = ''
    if tags:
        for tag in tags:
            if key in tag['Key']:
                value = tag['Value']
    return value

def has_public_route(routes):
    """
    Returns true if the the route table is public
    """
    if routes:
        for route in routes:
            if 'igw-' in route.get('GatewayId', ''): # and route.get('DestinationCidrBlock') == '0.0.0.0/0':
                return True

def get_route_tables(session, vpc_id):
    """
    Returns a list of route tables for the vpc id
    """
    client = session.client('ec2')
    route_tables = client.describe_route_tables(**filter_vpc_id(vpc_id))['RouteTables']
    return route_tables

def get_main_route_table(session, vpc_id):
    """
    Returns the  main route table
    """
    client = session.client('ec2')
    rtbl_filter = filter_vpc_id(vpc_id)
    rtbl_filter['Filters'].append({'Name': 'association.main', 'Values': ['true']})
    route_table = client.describe_route_tables(**rtbl_filter)['RouteTables']
    return route_table

def get_public_route_tables(session, vpc_id):
    """
    Returns a list of public route tables
    """

    route_tables = get_route_tables(session, vpc_id)
    public_route_tables = [rtb for rtb in route_tables if has_public_route(rtb.get('Routes'))]
    return public_route_tables

def get_route_table_association(subnet_id, route_tables):
    """
    Returns route table associations for the given subnet and route tables
    """
    for rtb in route_tables:
        for association in rtb['Associations']:
            if association.get('SubnetId', '') == subnet_id:
                return rtb


def get_public_subnet_ids(session, vpc_id):
    """
    1. is the subnet associated to a route table
    2. if no check if the main route table is public
    3. if yes check if the subnet is associated to a public route table
    """
    route_tables = get_route_tables(session, vpc_id)
    main_route_table = get_main_route_table(session, vpc_id)
    public_route_tables = get_public_route_tables(session, vpc_id)

    client = session.client('ec2')
    public_subnets = []
    public_subnet_ids = []
    subnets = sorted(
        client.describe_subnets(**filter_vpc_id(vpc_id))['Subnets'],
        key=itemgetter('AvailabilityZone')
    )
    
    for subnet in subnets:
        # if the subnet is not explicitly associated to any route tables, it indirectly associates to the main route table
        if not get_route_table_association(subnet['SubnetId'], route_tables):
            if has_public_route(main_route_table[0].get('Routes')):
                public_subnets.append(subnet)
                public_subnet_ids.append(subnet['SubnetId'])

        if get_route_table_association(subnet['SubnetId'], public_route_tables):
            public_subnets.append(subnet)
            public_subnet_ids.append(subnet['SubnetId'])

    return public_subnet_ids

def get_first_public_subnet_id(session, vpc_id):
    """
    Returns the first public subnet ordered by az
    """
    public_subnet_ids = get_public_subnet_ids(session, vpc_id)
    if public_subnet_ids:
        return public_subnet_ids[0]

def get_security_group_ids(session, vpc_id):
    """
    Returns a list of security group ids minus the bastion sg
    """
    exclude_tag=config.cli_tag_key
    client = session.client('ec2')
    security_groups = client.describe_security_groups(**filter_vpc_id(vpc_id))['SecurityGroups']
    security_group_ids = [sg['GroupId'] for sg in security_groups if not get_tag_value(sg.get('Tags'), key=exclude_tag)]
    return security_group_ids

def get_subnets(session):
    """
    """
    

def get_vpc_summary(session, vpc_id):
    """
    """
    client = session.client('ec2')
    vpc = client.describe_vpcs(**filter_vpc_id(vpc_id))['Vpcs']

def get_in_use_enis(session, vpc_id):
    """

    """
    client = session.client('ec2')
    eni_filter = filter_vpc_id(vpc_id)
    eni_filter['Filters'].append({'Name': 'status', 'Values': ['in-use']})
    enis = client.describe_network_interfaces(**eni_filter)['NetworkInterfaces']
    return enis

def count_eip_enis(enis):
    """
    Returns the count of of enis with an elastic ip (primary ip only)
    """
    eni_eips = []
    for eni in enis:
        association = eni.get('Association')
        if association:
            if association['IpOwnerId'] != 'amazon':
                eni_eips.append(eni)
    return len(eni_eips)

def count_public_enis(enis):
    """
    Returns the count of enis with a public ip (elastic ip or amazon owned ip) (primary ip only)
    """
    public_enis = [eni for eni in enis if eni.get('Association')]
    return len(public_enis)


def count_private_enis(enis):
    """
    Returns the count of enis without a public ip. (primary ip only)
    """
    private_enis = [eni for eni in enis if not eni.get('Association')]
    return len(private_enis)

def has_natgw(session, vpc_id):
    """
    Returns true if a nat gw is associated to the vpc
    """
    has_nat_gateway = False
    client = session.client('ec2')
    nat_gateways = client.describe_nat_gateways(**filter_vpc_id(vpc_id))['NatGateways']
    if nat_gateways:
        has_nat_gateway = True
    return has_nat_gateway

def has_igw(session, vpc_id):
    """
    Returns true if an igw is attached to the vpc
    """
    has_igw = False
    igw_filter = {'Filters': [{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]}
    client = session.client('ec2')
    igw = client.describe_internet_gateways(**igw_filter)['InternetGateways']
    if igw:
        has_igw = True
    return has_igw

def get_vpcs(session):
    """
    Returns a list of vpcs information
    """
    client = session.client('ec2')
    vpcs = client.describe_vpcs()['Vpcs']
    records = []
    for vpc in vpcs:
        in_use_enis = get_in_use_enis(session, vpc['VpcId'])
        subnets = client.describe_subnets(**filter_vpc_id(vpc['VpcId']))['Subnets']
        vpc_tags = vpc.get('Tags', [])

        records.append(OrderedDict([
            ('vpc_id', vpc['VpcId']),
            ('tag_name', get_tag_value(vpc_tags)),
            ('cidr', vpc['CidrBlock']),
            ('default_vpc', vpc['IsDefault']),
            ('has_natgw', has_natgw(session, vpc['VpcId'])),
            ('has_igw', has_igw(session, vpc['VpcId'])),
            ('enis_prv', count_private_enis(in_use_enis)),
            ('enis_pub', count_public_enis(in_use_enis)),
            ('eni_eips', count_eip_enis(in_use_enis)),
            ('enis_total', len(in_use_enis)),
            ('sgs_total', len(get_security_group_ids(session, vpc['VpcId']))),
            ('subnets_pub', len(get_public_subnet_ids(session, vpc['VpcId']))),
            ('subnets_total', len(subnets)),
        ]))
    return records

def get_instances(session):
    """
    """
    client = session.client('ec2')
    reservations = client.describe_instances()['Reservations']
    instances = [
        instance for reservation in reservations
        for instance in reservation['Instances']
    ]
    return instances

def is_bastion_instance(session, name, instance):
    """
    Returns true if the instance is a bastion.
    """
    is_bastion = False
    has_cli_tag = get_tag_value(instance.get('Tags'), config.cli_tag_key)
    has_name_tag = get_tag_value(instance.get('Tags'))
    state = instance['State']['Name']
    if has_cli_tag and has_name_tag and state == 'running':
        is_bastion = True
    return is_bastion

@ec2_patching.keypairs.add_ssh_keys_fingerprints
def get_vpc_instances(session, vpc_id, path=None, detailed=False, bastion_name=None):
    """
    """
    client = session.client('ec2')
    instances = get_instances(session)
    if vpc_id:
        instances = [instance for instance in instances if instance.get('VpcId') == vpc_id]

    records = []
    for instance in instances:
        logger.debug('instance: {}'.format(instance))
        if detailed:
              records.append(OrderedDict([
                  ('launch_time', instance.get('LaunchTime')),
                  ('vpc_id', instance.get('VpcId')),
                  ('instance_id', instance['InstanceId']),
                  ('state', instance['State']['Name']),
                  ('platform', instance.get('Platform')),
                  ('tag_name', get_tag_value(instance.get('Tags'))),
                  ('public_ip', instance.get('PublicIpAddress')),
                  ('private_ip', instance.get('PrivateIpAddress')),
                  ('key_pair', instance.get('KeyName', '')),
                  ('bastion', is_bastion_instance(session, bastion_name, instance)),
                  ('ami', instance.get('ImageId')),
                  ('ami_name', get_ami_name(session, instance.get('ImageId'))),
              ]))

        else:
            records.append(OrderedDict([
                ('vpc_id', instance.get('VpcId')),
                ('instance_id', instance['InstanceId']),
                ('tag_name', get_tag_value(instance.get('Tags'))),
                ('private_ip', instance.get('PrivateIpAddress')),
                ('key_pair', instance.get('KeyName', '')),
            ]))

    logger.debug(records)
    return records

def stop_ec2_instance(session, instance_id):
    """
    Stop the bastion ec2 instance.
    """
    client = session.client('ec2')
    logger.info('stopping instance: {}'.format(instance_id))
    client.stop_instances(InstanceIds=[instance_id])

def start_ec2_instance(session, instance_id):
    """
    Start the bastion ec2 instance.
    """
    client = session.client('ec2')
    logger.info('starting instance: {}'.format(instance_id))
    client.start_instances(InstanceIds=[instance_id])
