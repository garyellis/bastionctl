from ec2_patching import aws
from ec2_patching import keypairs
from ec2_patching import cf_templates
from ec2_patching import cf
from ec2_patching import utils
import logging
import tabulate

logger = logging.getLogger(__name__)

# vpc group commands
def vpc_list(profile, region):
    """
    Lists vpcs info
    """
    session = aws.get_session(profile_name=profile, region_name=region)
    vpcs = aws.get_vpcs(session)
    print tabulate.tabulate(vpcs, headers='keys')

# bastion group commands
def gen_bastion_template(name, ami_id, instance_type, key_name, vpc_id, bastion_sg_ingress, profile, region):
    """
    Sets up the bastion template parameters and returns the bastion cloudformation template
    """

    if not key_name:
        key_name = name

    if not bastion_sg_ingress:
        logger.info('an allow-ip address was not provided. resolving public ip')
        bastion_sg_ingress = [utils.get_public_ip()]
        logger.info('allow ip address {}'.format(bastion_sg_ingress))

    session = aws.get_session(profile_name=profile, region_name=region)

    if not ami_id:
        ami = aws.get_default_ami(session)
        ami_id = ami['ImageId']
        logger.info('using default ami: ami_id: {} name: {}'.format(ami_id, ami['Name']))

    public_subnet_id = aws.get_first_public_subnet_id(session, vpc_id)
    security_group_ids = aws.get_security_group_ids(session, vpc_id)
    
    logger.info('using vpc_id: {}, subnet_id: {}'.format(vpc_id, public_subnet_id))
    logger.info('adding bastion private ip security group ingress rules on: {}'.format(' '.join(security_group_ids)))
    bastion_template = cf_templates.create_bastion_template(
        name=name,
        ami_id=ami_id,
        instance_type=instance_type,
        key_name=key_name,
        subnet_id=public_subnet_id,
        vpc_id=vpc_id,
        bastion_sg_ingress=bastion_sg_ingress,
        sg_ids=security_group_ids
    )

    cf.validate_template(session, bastion_template)
    return bastion_template

def create_bastion(name, ami_id, instance_type, key_name, ssh_public_key, vpc_id, bastion_sg_ingress, profile, region):
    """
    Creates the bastion keypair and cloudformation stack
    """
    session = aws.get_session(profile_name=profile, region_name=region)

    if not key_name and not ssh_public_key:
        logger.fatal('an ssh keypair name or ssh public key is required.')
        exit(1)
    if ssh_public_key:
        key_name = keypairs.import_keypair(session, name, ssh_public_key)

    template = gen_bastion_template(name, ami_id, instance_type, key_name, vpc_id, bastion_sg_ingress, profile, region)
    logger.info('creating the cloudformation stack {}'.format(name))

    # add stack tag to mark stacks created by the cli
    cf.create_stack(
        session,
        name,
        template,
    )

    stack_outputs = cf.get_stack_outputs(session, name)
    logger.info('stack outputs: {}'.format(stack_outputs))
    logger.info('bastion create complete')

def delete_bastion(delete_keypair, name, profile, region):
    """
    Deletes the bastion cloudformation stack and keypair
    """
    session = aws.get_session(profile_name=profile, region_name=region)

    if delete_keypair:
        keypairs.delete_keypair(session, name)

    logger.info('deleting the cloudformation stack {}'.format(name))

    # delete the stack if the stack was created by the cli
    
    cf.delete_stack(
        session,
        name
    )

def ssh(name, profile, region):
    """
    ssh into the bastion instance
    """
    session = aws.get_session(profile_name=profile, region_name=region)
    stack_outputs = cf.get_stack_outputs(session, name)
    #os.system('ssh -tt -A ubuntu@34.219.250.189')
