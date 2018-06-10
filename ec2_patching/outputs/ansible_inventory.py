import ec2_patching.outputs.decorators
import logging
import re
import yaml

log = logging.getLogger(__name__)

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
            log.info('matched {} in {}'.format(pattern, pattern))
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
           log.info('ansible_python_interpreter matched {} in {}'.format(pattern, ami_name))
           ansible_python_interpreter = python_interpreter
    return ansible_python_interpreter

@ec2_patching.outputs.decorators.add_bastion_flag
def create_host_inventory_item(record):
    """
    Configures the ansible inventory item
    """
    # ami_user and ansible_python_interpreter are commented until we setup a 'clean' way to
    # fetch the ami id. this is a result of field selectivity in the ec2 client module 'aws'


    log.info('create ansible inventory item for {}'.format(record['instance_id']))
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

    # determine the ssh user based on the ami name.
    # we should setup a toggle switch for this
    #ansible_user = resolve_ansible_user(record['ami_name'])
    #inventory_host_vars['ansible_user'] = ansible_user
    inventory_host_vars['ansible_user'] = 'ubuntu'

    # override the ansible interpreter when applicable. i.e. python3
    #ansible_python_interpreter = resolve_ansible_python_interpreter(record['ami_name'])
    ansible_python_interpreter = resolve_ansible_python_interpreter('xenial')
    if ansible_python_interpreter:
        inventory_host_vars['ansible_python_interpreter'] = ansible_python_interpreter

    log.info('created inventory item: {}'.format({ inventory_item_key : inventory_host_vars }))
    return { inventory_item_key : inventory_host_vars }

@ec2_patching.outputs.decorators.add_ssh_proxy
def to_inventory(records):
    """
    """
    log.info('configuring instances records to ansible_inventory')
    inventory = {
        'all': {
          'hosts': {}
        }
    }
    for i in records:
        ansible_host = create_host_inventory_item(i)
        inventory['all']['hosts'].update(ansible_host)

    return inventory

def to_yaml(items, filename):
    """
    """
    log.info('writing ansible inventory to {}'.format(filename))
    with open( filename, 'w') as s:
        yaml.safe_dump(items, s, default_flow_style=False, encoding='utf-8', allow_unicode=True)

