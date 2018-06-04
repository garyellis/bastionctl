import ec2_patching.commands
import ec2_patching.utils
import click



class Opts(object):
    def __init(self):
        self.profile = None
        self.region = None


pass_opts = click.make_pass_decorator(Opts, ensure=True)

@click.group()
@click.option(
    '--log-level',
    default='INFO',
    help='the logging level'
)
@click.option(
    '--profile',
    required=False,
    help='the aws credential profile')
@click.option(
    '--region',
    default='us-west-2',
    help='the aws region. Defaults to us-west-2'
)
@pass_opts
def cli(opts, log_level, profile, region):
    """
    """
    logger = ec2_patching.utils.setup_logging(log_level)
    logger.debug('log level: {}'.format(log_level))
    opts.profile = profile
    opts.region = region


@click.group(name='vpc')
def vpc_group():
    """
    Commands for viewing vpc resources
    """

@vpc_group.command(name='list')
@click.option('--name', help='filter vpcs by name')
@click.option('--cidr', help='filter vpcs by cidr')
@pass_opts
def vpcs_list(opts, name, cidr):
    """
    List vpcs
    """
    ec2_patching.commands.vpc_list(opts.profile, opts.region)

@click.group(name='bastion')
def bastion_group():
    """
    Commands for managing a bastion ec2 instance and security group rules
    """

@bastion_group.command(name='gen-template')
@click.option('--allow-ip', multiple=True, help='A list of CIDRs allowed by the bastion security group.')
@click.option('--ami-id', help='Defaults to latest Ubuntu xenial marketplace image.')
@click.option('--instance-type', default='t2.micro', help='the bastion instance type.')
@click.option('--key-name', help='the bastion instance key name')
@click.option('--name', required=True, help='the name of the bastion related resources')
@click.option('--vpc-id',required=True)
@pass_opts
def gen_template(opts, allow_ip, ami_id, instance_type, key_name, name, vpc_id):
    """
    Generates the bastion cloudformation template
    """

    bastion_template = ec2_patching.commands.gen_bastion_template(
        name=name,
        vpc_id=vpc_id,
        ami_id=ami_id,
        instance_type=instance_type,
        key_name=key_name,
        bastion_sg_ingress=allow_ip,
        profile=opts.profile,
        region=opts.region
    )
    print bastion_template

@bastion_group.command(name='create')
@click.option('--allow-ip', multiple=True, help='A list of CIDRs allowed by the bastion security group.')
@click.option('--ami-id', help='Defaults to latest Ubuntu xenial marketplace image.')
@click.option('--instance-type', default='t2.micro', help='The bastion instance type.')
@click.option('--key-name', help='the bastion instance key name',default=None)
@click.option('--name', required=True, help='the name of the bastion related resources')
@click.option('--ssh-public-key', help='import the ssh key', default=None)
@click.option('--vpc-id',required=True)
@pass_opts
def create_stack(opts, allow_ip, ami_id, instance_type, key_name, name, ssh_public_key, vpc_id):
    """
    Creates the bastion cloudformation stack
    """
    ec2_patching.commands.create_bastion(
        name=name,
        ami_id=ami_id,
        instance_type=instance_type,
        key_name=key_name,
        ssh_public_key=ssh_public_key,
        vpc_id=vpc_id,
        bastion_sg_ingress=allow_ip,
        profile=opts.profile,
        region=opts.region
    )

@bastion_group.command(name='delete')
@click.option('--delete-keypair/--no-delete-keypair', default=False, help='delete the imported bastion keypair')
@click.option('--name', required=True, help='the name of the bastion cloudformation stack')
@pass_opts
def delete_stack(opts, delete_keypair, name):
    """
    Deletes the bastion cloudformation stack
    """
    ec2_patching.commands.delete_bastion(
        delete_keypair=delete_keypair,
        name=name,
        profile=opts.profile,
        region=opts.region
    )

@bastion_group.command(name='list')
@pass_opts
def list_stacks(opts):
    """
    List bastions
    """
    ec2_patching.commands.list_bastion(
        profile=opts.profile,
        region=opts.region,
    )

@bastion_group.command(name='ssh')
@click.option('--name', help='the name of the bastion cloudformation stack')
@click.option('--user', default='ubuntu', help='the bastion ssh user')
@pass_opts
def list_stacks(opts, name, user):
    """
    ssh into the bastion instance
    """
    ec2_patching.commands.ssh(
        profile=opts.profile,
        region=opts.region,
        name=name,
        user=user
    )

cli.add_command(bastion_group)
cli.add_command(vpc_group)
