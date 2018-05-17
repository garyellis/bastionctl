import boto3
from botocore.exceptions import ClientError
from operator import itemgetter

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


def get_first_public_subnet_id(session, vpc_id):
    """
    Returns the first public subnet id ordered by az
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

    # if the list is empty we could not find a public subnet
    if public_subnet_ids:
        return public_subnet_ids[0]

def get_security_group_ids(session, vpc_id):
    """
    Returns a list of security group ids
    """
    exclude_tag='aws-patching'
    client = session.client('ec2')
    security_groups = client.describe_security_groups(**filter_vpc_id(vpc_id))['SecurityGroups']
    security_group_ids = [sg['GroupId'] for sg in security_groups if not get_tag_value(sg.get('Tags'), key=exclude_tag)]
    return security_group_ids
