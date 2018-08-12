import tabulate
import logging
import logging.config
import requests
import csv
import json
import yaml


logger = logging.getLogger(__name__)


def setup_logging(log_level):
    """
    """
    if log_level in ['INFO', 'CRITICAL']:
        logging.getLogger('botocore').setLevel(logging.CRITICAL)
    if log_level in ['DEBUG']:
        logging.getLogger('botocore').setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)4s %(name)4s [%(filename)s:%(lineno)s - %(funcName)s()] %(levelname)4s %(message)4s'))
    logger = logging.getLogger('bastionctl')
    logger.addHandler(handler)
    logger.setLevel(log_level)
    return logger


def get_public_ip():
    """
    Returns the public ipv4 ip
    """
    logger = logging.getLogger(__name__)
    ip_addr_url = 'https://api.ipify.org'

    logger.info('getting public ipv4 address from {}'.format(ip_addr_url))
    ip = requests.get(ip_addr_url).text
    logger.info('public ip is {}'.format(ip))

    if ip:
        ip_cidr = '{}/32'.format(ip)
        return ip_cidr


def to_table(items):
    """
    """
    print tabulate.tabulate(
        tabular_data=items,
        headers='keys'
    )


def to_csv(content, filename, append=False, keys=[]):
    """
    """
    if not keys:
        keys = sorted(content[0].keys())

    with open(filename, 'w') as stream:
        csv_writer = csv.DictWriter(stream, keys)
        csv_writer.writeheader()
        csv_writer.writerows(content)


def to_yaml(items, filename):
    """
    """
    # convert ordered dict to regular dict to bypass adding yaml representer
    i = json.loads(json.dumps(items))

    opts = dict(default_flow_style=False, encoding='utf-8', allow_unicode=True)
    if not filename:
        print yaml.safe_dump(data=i, stream=None, **opts)
    else:
        logger.info('writing file to {}'.format(filename))
        with open(filename, 'w') as s:
            yaml.safe_dump(data=i, stream=s, **opts)


def to_json(items, filename):
    """
    """
    if not filename:
        print json.dumps(items)
    else:
        with open(filename, 'w') as s:
            logger.info('writing json to {}'.format(filename))
            json.dump(items, filename)


def output(items, output_format, filename=None):
    """
    """
    if output_format == 'table':
        to_table(items=items)

    elif output_format == 'json':
        to_json(items, filename)

    elif output_format == 'yaml':
        to_yaml(items, filename)

    elif output_format == 'csv':
        to_csv(content=items, filename=filename)
