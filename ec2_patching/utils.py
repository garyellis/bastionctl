import logging
import logging.config
import requests

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
    logger = logging.getLogger('ec2_patching')
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
