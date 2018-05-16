import aws_patching.bastion
import click

class Opts(object):
    def __init(self):
        self.profile = None
        self.region = None


pass_opts = click.make_pass_decorator(Opts, ensure=True)

@click.group()
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
def cli(opts, profile, region):
    opts.profile = profile
    opts.region = region

@cli.command()
@click.argument(
    'action',
    type=click.Choice(['create', 'destroy', 'get-template']),
)
@click.option('--allow-ip', help='the bastion ingress ip address')
@click.option('--ami-id', help='deploy the basiton using the given ami id')
@click.option('--name', help='the name of the bastion related resources')
@click.option('--vpc-id',required=True)
@pass_opts
def bastion(opts, action, allow_ip, ami_id, name, vpc_id):
    """
    Work with the bastion
    """

    # this is a little too hard coded.
    # we should instead use introspectionu i.e. getattr to construct the function to call.
    # or we reorganize cli to map cli command to a module function
    if action in 'get-template':
        bastion_template = aws_patching.bastion.get_bastion_template(
            name=name,
            vpc_id=vpc_id,
            bastion_sg_ingress=allow_ip,
            profile=opts.profile,
            region=opts.region
        )
        print bastion_template
    else:
        print 'action: {} is not yet implemented'.format(action)

