import bastionctl.config as config
from functools import wraps
import logging
import re

logger = logging.getLogger(__name__)


def sanitize_name(name):
    """
    Strips any spaces, tabs and newlines and lowers case
    """
    sanitized_name = ''
    if name:
        sanitized_name = re.sub(r'[\n\t\s]*', '', name.lower())
    return sanitized_name


def resolve_ansible_user(ami_name):
    """
    """
    # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html
    ansible_user = 'ec2-user'
    ami_users = {
        'admin': '(debian)',
        'ubuntu': '(ubuntu|xenial|trusty|precise|bionic|beaver)',
        'centos': 'cent',
        'fedora': 'fedora',
        'ec2-user': '(amz|ecs|elasticbeanstalk|emr|amazon|rhel)'
    }
    for user, pattern in ami_users.iteritems():
        match = re.search(r'{}'.format(pattern), ami_name, re.IGNORECASE)
        if match:
            logger.info('matched {} in {}'.format(pattern, pattern))
            ansible_user = user

    return ansible_user


def resolve_ansible_python_interpreter(ami_name):
    """
    """
    ansible_python_interpreter = ''
    python_interpreters = {
        '/usr/bin/python3': '(xenial|bionic|beaver|artful)'
    }
    for python_interpreter, pattern in python_interpreters.iteritems():
        match = re.search(pattern, ami_name, re.IGNORECASE)
        if match:
            logger.info('ansible_python_interpreter matched {} in {}'.format(
                pattern, ami_name
            ))
            ansible_python_interpreter = python_interpreter
    return ansible_python_interpreter


def mark_bastion_inventory_item(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        record = kwargs.get('record')

        inventory_item = f(*args, **kwargs)
        name = inventory_item.keys()[0]

        if record.get('bastion'):
            logger.info('found bastion. configuring public ip...')
            inventory_item[name].update(
                {
                  'ansible_host': record.get('public_ip'),
                  config.cli_tag_key: config.cli_tag_value
                }
            )
            logger.info('bastion: {}'.format(inventory_item))

        return inventory_item
    return wrapped


def is_bastion(record):
    """
    """
    logger.info('checking if is bastion: {}'.format(record))
    for v in record.values():
        if v.get(config.cli_tag_key):
            return True


def bastion_ssh_args(record):
    """
    """
    ansible_ssh_common_args = None
    for v in record.values():
        ansible_ssh_common_args = "-o ProxyCommand=\"ssh -A -W %h:%p -q {}@{}\"".format(
            v['ansible_user'],
            v['ansible_host']
        )
    if ansible_ssh_common_args:
        return ansible_ssh_common_args


@mark_bastion_inventory_item
def create_host_inventory_item(record):
    """
    Configures the ansible inventory item
    """

    logger.info('create ansible inventory item for {}'.format(record['instance_id']))
    inventory_host_vars = {}
    inventory_item_key = ''

    # setup the inventory item name
    if record.get('tag_name'):
        _inventory_item_key = '{}.{}'.format(record['tag_name'],record['instance_id'])
        inventory_item_key = sanitize_name(_inventory_item_key)
    else:
        inventory_item_key = record['instance_id']

    # setup aws host vars
    inventory_host_vars.update({ 'instance_id': record['instance_id']})

    # setup the ansible_host variables
    inventory_host_vars['ansible_host'] = record['private_ip']

    if record.get('private_key_file'):
        inventory_host_vars['ansible_ssh_private_key_file'] = record['private_key_file']

    # determine the ssh user based on the ami name. this should be made optional
    ansible_user = resolve_ansible_user(record['ami_name'])
    inventory_host_vars['ansible_user'] = ansible_user

    # override the ansible interpreter when applicable. i.e. python3
    ansible_python_interpreter = resolve_ansible_python_interpreter(record['ami_name'])
    if ansible_python_interpreter:
        inventory_host_vars['ansible_python_interpreter'] = ansible_python_interpreter

    logger.info('created inventory item: {}'.format({ inventory_item_key : inventory_host_vars }))
    return { inventory_item_key : inventory_host_vars }


def to_inventory(records, group_name):
    """
    """
    logger.info('configuring instances records to ansible_inventory')
    inventory = {
        'all': {
          'children': {
            group_name: {
              'vars': {},
              'hosts': {}
            }
          }
        }
    }

    for i in records:
        ansible_host = create_host_inventory_item(record=i)
        if is_bastion(ansible_host):
            bastion_group_name = '{}-bastion'.format(group_name)
            inventory['all']['children'][bastion_group_name] = {
              'hosts': ansible_host
            }

            inventory['all']['children'][group_name]['vars'].update({
                'ansible_ssh_common_args': bastion_ssh_args(ansible_host)
            })
        else:
            inventory['all']['children'][group_name]['hosts'].update(ansible_host)

    return inventory
