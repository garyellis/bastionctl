import ec2_patching.config as config
import ec2_patching.aws
import ec2_patching.cf
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def setup_bastion_inventory(f):
  @wraps(f)
  def wrapped(*args, **kwargs):
      record = kwargs.get('record')

      inventory_item = f(*args, **kwargs)
      name = inventory_item.keys()[0]
      inventory_instance_id = inventory_item[name]['instance_id']

      if record.get('bastion'):
          logger.info('found bastion. configuring public ip...')
          inventory_item[name].update({ 'ansible_host': record.get('public_ip'), config.cli_tag_key: config.cli_tag_value})
          logger.info('bastion: {}'.format(inventory_item))

      return inventory_item
  return wrapped

def add_ssh_proxy(f):
  @wraps(f)
  def wrapped(*args, **kwargs):
    records = kwargs.get('records')
    inventory = f(*args, **kwargs)

    bastion = {k:v for k,v in inventory['all']['hosts'].items() if v.get(config.cli_tag_key)}
    bastion = bastion.itervalues().next()

    logger.info('adding proxy: {}'.format(bastion))
    for inventory_name in inventory['all']['hosts'].keys():
        logger.info('working on: {}'.format(inventory_name))
        if bastion and not inventory['all']['hosts'][inventory_name].get(config.cli_tag_key):
          ansible_ssh_common_args = "-o ProxyCommand=\"ssh -A -W %h:%p -q {}@{}\"".format(bastion['ansible_user'], bastion['ansible_host'])
          logger.info('ansible_ssh_args: {}'.format(ansible_ssh_common_args))
          inventory['all']['hosts'][inventory_name].update({'ansible_ssh_common_args': ansible_ssh_common_args})

    return inventory
  return wrapped
