from ec2_patching import aws
from ec2_patching import cf_templates


# bastion group commands
def gen_bastion_template(name, ami_id, instance_type, key_name, vpc_id, bastion_sg_ingress, profile, region):
    """
    Sets up the bastion template parameters and returns the bastion cloudformation template
    """
    session = aws.get_session(profile_name=profile, region_name=region)
    public_subnet_id = aws.get_first_public_subnet_id(session, vpc_id)
    security_group_ids = aws.get_security_group_ids(session, vpc_id)
   
    return cf_templates.create_bastion_template(
        name=name,
        ami_id=ami_id,
        instance_type=instance_type,
        key_name=key_name,
        subnet_id=public_subnet_id,
        vpc_id=vpc_id,
        bastion_sg_ingress=bastion_sg_ingress,
        sg_ids=security_group_ids
    )

def create_bastion_stack(name, vpc_id, bastion_sg_ingress, profile, region):
    """
    Creates the bastion cloudformation stack
    """
    template = get_bastion_template(name, vpc_id, bastion_sg_ingress, profile, region=region)
    print 'create the bastion cloudformation stack placeholder'

def delete_bastion_stack(name, profile, region):
    """
    Deletes the bastion cloudformation stack
    """

    print 'delete the cloudformation stack placeholder'
