import ec2_patching.config as config
import ec2_patching.aws
import ec2_patching.cf
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def is_bastion_instance(instance_id):
    """
    Returns true if the instance is a bastion.
    """
    # this function gets configuration state module set by the cli
    # we should use the state sparingly and be consistent with function input/outputs
    bastion_instances = []
    session = ec2_patching.aws.get_session(config.opts.profile, config.opts.region)
    instances = ec2_patching.aws.get_instances(session)
    for instance in instances:
        is_bastion = ec2_patching.aws.get_tag_value(instance.get('Tags'), config.cli_tag_key)
        if is_bastion and instance['InstanceId'] == instance_id:
            return True

def get_bastion_from_inventory(inventory):
    """
    """
    for inventory_name in inventory['all']['hosts'].keys():
        inventory_item = inventory['all']['hosts'][inventory_name]
        if inventory_item.get(config.cli_tag_key):
            return inventory_item

def get_bastion_ip_from_stack(name):
    """
    Returns the bastion ip address
    """
    session = ec2_patching.aws.get_session(config.opts.profile, config.opts.region)
    stack_outputs = ec2_patching.cf.get_stack_outputs(session, name)
    public_ip = ec2_patching.cf.get_stack_output_value(stack_outputs, config.stack_output_public_ip_key)
    return public_ip

# we setup the following  decorators to help keep the outputs.ansible_inventory module focused on generating our ansible inventory file

def add_bastion_flag(f):
  @wraps(f)
  def wrapped(*args, **kwargs):
      inventory_item = f(*args, **kwargs)
      name = inventory_item.keys()[0]
      inventory_instance_id = inventory_item[name]['instance_id']

      if is_bastion_instance(inventory_instance_id):
          # setup the bastion public ip address as part of flagging the bastion
          inventory_item[name].update({ config.cli_tag_key: 'true'})
          logger.info('marked bastion {}'.format(inventory_item))


      return inventory_item
  return wrapped

def add_ssh_proxy(f):
  @wraps(f)
  def wrapped(*args, **kwargs):
    inventory = f(*args, **kwargs)
    bastion = get_bastion_from_inventory(inventory)
    logger.info('adding proxy: {}'.format(bastion))
    for inventory_name in inventory['all']['hosts'].keys():
        logger.info('working on: {}'.format(inventory_name))
        if bastion and not inventory['all']['hosts'][inventory_name].get(config.cli_tag_key):
          ansible_ssh_args = '-o ProxyCommand="ssh -A -W %h:%p -q {}@{}"'.format(bastion['ansible_host'], bastion['ansible_user'])
          inventory['all']['hosts'][inventory_name].update({'ansible_ssh_args': ansible_ssh_args})

    return inventory
  return wrapped
