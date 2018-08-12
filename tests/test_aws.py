import bastionctl.aws
import boto3
import pytest
from moto import mock_ec2


@pytest.fixture
def get_tags_data():
    """
    """
    return [
        {'Key': 'Name', 'Value': 'Foo'},
        {'Key': 'Test', 'Value': 'Bar'}
    ]


@pytest.fixture
def get_ami_data():
    """
    """
    return {
        'ami_id': 'ami-785db401',
        'ami_name': 'ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20170721'
    }


class TestAws(object):
    def setup_method(self, test_method):
        self.session = bastionctl.aws.get_session(profile_name=None)

    def test_get_tag_value_default(self, get_tags_data):
        tags = get_tags_data
        tag_value = bastionctl.aws.get_tag_value(tags=tags)
        assert tag_value == 'Foo'

    def test_get_tag_value(self, get_tags_data):
        tags = get_tags_data
        tag_value = bastionctl.aws.get_tag_value(
            tags=tags,
            key='Test'
        )
        assert tag_value == 'Bar'

    @mock_ec2
    def test_get_default_ami(self):
        ami = bastionctl.aws.get_default_ami(self.session)
        assert 'ImageId' in ami

    @mock_ec2
    def test_get_ami_id(self, get_ami_data):
        ami_name = bastionctl.aws.get_ami_name(
            self.session,
            get_ami_data['ami_id']
        )
        assert get_ami_data['ami_name'] == ami_name

    @mock_ec2
    def test_get_route_tables(self):
        client = boto3.client('ec2')
        vpcs = client.describe_vpcs()['Vpcs']
        route_tables = bastionctl.aws.get_route_tables(
            session=self.session,
            vpc_id=vpcs[0]['VpcId']
        )
        assert 'rtb' in route_tables[0]['RouteTableId']

    @mock_ec2
    def test_get_public_route_tables(self):
        client = boto3.client('ec2')
        vpcs = client.describe_vpcs()['Vpcs']
        public_route_tables = bastionctl.aws.get_public_route_tables(
            session=self.session,
            vpc_id=vpcs[0]['VpcId']
        )
        assert len(public_route_tables) == 0

    @mock_ec2
    def test_get_vpcs(self):
        vpcs = bastionctl.aws.get_vpcs(
            session=self.session,
        )

        assert 'cidr' in vpcs[0]
        assert 'enis_total' in vpcs[0]
        assert 'sgs_total' in vpcs[0]
        assert 'subnets_pub' in vpcs[0]
        assert 'subnets_total' in vpcs[0]
        assert 'tag_name' in vpcs[0]
        assert 'vpc_id' in vpcs[0]
