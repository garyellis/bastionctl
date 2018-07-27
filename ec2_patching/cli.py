import ec2_patching.config as config
import ec2_patching.commands
import ec2_patching.utils
import click


class Opts(object):
    def __init(self):
        self.profile = None
        self.region = None


pass_opts = click.make_pass_decorator(Opts, ensure=True)


@click.group(invoke_without_command=True)
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
@click.option(
    '--version',
    is_flag=True,
    default=False,
    help='Version of this utility'
)
@pass_opts
def cli(opts, log_level, profile, region, version):
    """
    """
    logger = ec2_patching.utils.setup_logging(log_level)
    logger.debug('log level: {}'.format(log_level))
    opts.profile = profile
    opts.region = region
    # set state in config module
    config.opts = opts
    if version:
      click.echo(ec2_patching.config.cli_version)


@click.group(name='instances')
def instances_group():
    """
    Commands for viewing and exporting instances resources
    """


@instances_group.command(name='list')
@click.option(
    '--vpc-id',
    help='filter vpcs by vpc id'
)
@click.option(
    '--name',
    help='filter vpcs by associated bastion'
)
@click.option(
    '--ssh-keys-path',
    help='ssh keys path'
)
@click.option(
    '--detailed/--no-detailed',
    default=False,
    help='output detailed instances info'
)
@pass_opts
def instances_list(opts, name, vpc_id, ssh_keys_path, detailed):
    """
    List instances
    """
    ec2_patching.commands.instances_list(
        profile=opts.profile,
        region=opts.region,
        vpc_id=vpc_id,
        ssh_keys_path=ssh_keys_path,
        detailed=detailed
    )


@instances_group.command(name='gen-ansible-inventory')
@click.option(
    '--vpc-id',
    help='filter vpcs by vpc id'
)
@click.option(
    '--name',
    help='filter vpcs by associated bastion'
)
@click.option(
    '--ssh-keys-path',
    help='ssh keys path'
)
@click.option(
    '--out',
    help='the output filename'
)
@pass_opts
def instances_gen_ansible_inventory(opts, name, vpc_id, ssh_keys_path, out):
    """
    Generate an ansible inventory file
    """
    ec2_patching.commands.instances_gen_ansible_inventory(
        profile=opts.profile,
        region=opts.region,
        vpc_id=vpc_id,
        name=name,
        ssh_keys_path=ssh_keys_path,
        filename=out
    )


@click.group(name='vpc')
def vpc_group():
    """
    Commands for viewing vpc resources
    """


@vpc_group.command(name='list')
@click.option(
    '--name',
    help='filter vpcs by name'
)
@click.option(
    '--cidr',
    help='filter vpcs by cidr'
)
@click.option(
    '--fmt',
    default='table',
    help='the output format'
)
@pass_opts
def vpcs_list(opts, name, cidr, fmt):
    """
    List vpcs
    """
    ec2_patching.commands.vpc_list(
        profile=opts.profile,
        region=opts.region,
        output_format=fmt
    )


@click.group(name='bastion')
def bastion_group():
    """
    Commands for managing a bastion ec2 instance and security group rules
    """


@bastion_group.command(name='gen-template')
@click.option(
    '--allow-ip',
    multiple=True,
    help='A list of CIDRs allowed by the bastion security group.'
)
@click.option(
    '--ami-id',
    help='Defaults to latest Ubuntu xenial marketplace image.'
)
@click.option(
    '--instance-type',
    default='t2.micro',
    help='the bastion instance type.'
)
@click.option(
    '--key-name',
    help='the bastion instance key name'
)
@click.option(
    '--name',
    required=True,
    help='the name of the bastion related resources'
)
@click.option(
    '--vpc-id',
    required=True
)
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
@click.option(
    '--allow-ip',
    multiple=True,
    help='A list of CIDRs allowed by the bastion security group.'
)
@click.option(
    '--ami-id',
    help='Defaults to latest Ubuntu xenial marketplace image.'
)
@click.option(
    '--instance-type',
    default='t2.micro',
    help='The bastion instance type.'
)
@click.option(
    '--key-name',
    help='use an existing keypair name',
    default=None
)
@click.option(
    '--name',
    required=True,
    help='the name of the bastion related resources'
)
@click.option(
    '--ssh-public-key',
    help='import the basiton instance keypair',
    default=None
)
@click.option(
    '--vpc-id',
    required=True
)
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
@click.option(
    '--name',
    required=True,
    help='the name of the bastion cloudformation stack'
)
@pass_opts
def delete_stack(opts, name):
    """
    Deletes the bastion cloudformation stack
    """
    ec2_patching.commands.delete_bastion(
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


@bastion_group.command(name='stop')
@click.option(
    '--name',
    help='the name of the bastion cloudformation stack'
)
@pass_opts
def stop_bastion(opts, name):
    """
    Stop the bastion stack ec2 instance
    """
    ec2_patching.commands.stop_bastion(
        profile=opts.profile,
        region=opts.region,
        name=name
    )


@bastion_group.command(name='start')
@click.option(
    '--name',
    help='the name of the bastion cloudformation stack'
)
@pass_opts
def start_bastion(opts, name):
    """
    Start the bastion stack ec2 instance
    """
    ec2_patching.commands.start_bastion(
        profile=opts.profile,
        region=opts.region,
        name=name
    )


@bastion_group.command(name='ssh')
@click.option(
    '--name',
    help='the name of the bastion cloudformation stack'
)
@click.option(
    '--user',
    default='ubuntu',
    help='the bastion ssh user'
)
@pass_opts
def bastion_ssh(opts, name, user):
    """
    ssh into the bastion instance
    """
    ec2_patching.commands.ssh(
        profile=opts.profile,
        region=opts.region,
        name=name,
        user=user
    )


cli.add_command(instances_group)
cli.add_command(bastion_group)
cli.add_command(vpc_group)
