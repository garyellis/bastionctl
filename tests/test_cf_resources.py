from bastionctl import cf_resources
from troposphere import Template
from moto import mock_cloudformation


class TestCfTemplate(object):
    def setup_method(self):
        self.template = Template()

    @mock_cloudformation
    def test_ec2_resource(self, cf_client, vpc_data):
        ec2_resource = cf_resources.ec2_instance(
            name='test-ec2-bastion-cli',
            ami_id='ami-12345',
            keyname='foo',
            instance_type='t2.micro',
            sg_ids=['sg-12345'],
            subnet_id='subnet-12345'
        )

        self.template.add_resource(ec2_resource)
        cf_client.create_stack(
            StackName='test_ec2_resource',
            TemplateBody=self.template.to_yaml()
        )

#    @mock_cloudformation
#    def test_security_group_resource(self):
#        sg_resource = cf_resources.security_group(
#            name='test-security-group',
#            desc='test security group',
#            vpc_id='vpc-12345'
#        )
#        self.template.add_resource(sg_resource)
#        self.cf_client.create_stack(
#          StackName='test-ec2-resource',
#          TemplateBody=self.template.to_yaml()
#        )
