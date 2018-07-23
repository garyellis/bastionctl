import ec2_patching.aws
import ec2_patching.config as config
import mock
import pytest
from moto import mock_ec2


class TestAws(object):
    def setup_method(self, test_method):
        self.session = ec2_patching.aws.get_session(profile_name=None)
        self.test_ami_id = 'ami-785db401'
        self.test_ami_name = 'ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20170721'

    def teardown_method(self, test_method):
        pass

    def test_get_tag_value_default(self):
        tags = [
            { 'Key': 'Name', 'Value': 'Foo' },
            { 'Key': 'Test', 'Value': 'Bar' }
        ]
        tag_value = ec2_patching.aws.get_tag_value(tags=tags)
        assert tag_value == 'Foo'

    def test_get_tag_value(self):
        tags = [
            { 'Key': 'Name', 'Value': 'Foo' },
            { 'Key': 'Test', 'Value': 'Bar' }
        ]
        tag_value = ec2_patching.aws.get_tag_value(
            tags=tags,
            key='Test'
        )
        assert tag_value == 'Bar'

    @mock_ec2
    def test_get_default_ami(self):
        ami = ec2_patching.aws.get_default_ami(self.session)
        assert 'ImageId' in ami

    @mock_ec2
    def test_get_ami_id(self):
        ami_id = ec2_patching.aws.get_ami_name(
            self.session,
        self.test_ami_id)
        assert self.test_ami_name == ami_id

    @mock_ec2
    def test_get_route_tables(self):
        client = self.session.client('ec2')
        vpcs = client.describe_vpcs()['Vpcs']
        route_tables = ec2_patching.aws.get_route_tables(
            session=self.session,
            vpc_id=vpcs[0]['VpcId']
        )
        assert 'rtb' in route_tables[0]['RouteTableId']

    @mock_ec2
    def test_get_vpcs(self):
        vpcs = ec2_patching.aws.get_vpcs(
            session=self.session,
        )

        assert 'cidr' in vpcs[0]
        assert 'enis_total' in vpcs[0]
        assert 'sgs_total' in vpcs[0]
        assert 'subnets_pub' in vpcs[0]
        assert 'subnets_total' in vpcs[0]
        assert 'tag_name' in vpcs[0]
        assert 'vpc_id' in vpcs[0]
        
