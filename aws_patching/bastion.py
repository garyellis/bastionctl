import aws
import cf_templates

def get_bastion_template(name, vpc_id, bastion_sg_ingress, profile, region='us-west-2'):
    """
    Sets up the bastion template parameters and returns the bastion cloudformation template
    """
    session = aws.get_session(profile_name=profile, region_name=region)
    public_subnet_id = aws.get_first_public_subnet_id(session, vpc_id)
    security_group_ids = aws.get_security_group_ids(session, vpc_id)
   
    return cf_templates.create_bastion_template(
        name=name,
        ami_id='ami-123456',
        instance_type='t2.small',
        subnet_id=public_subnet_id,
        vpc_id=vpc_id,
        bastion_sg_ingress=bastion_sg_ingress,
        sg_ids=security_group_ids
    )
