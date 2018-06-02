import logging
import requests

logger = logging.getLogger(__name__)

def get_public_ip():
    """
    Returns the public ipv4 ip
    """
    ip_addr_url = 'https://api.ipify.org'

    logger.info('getting public ipv4 address from {}'.format(ip_addr_url))
    ip = requests.get(ip_addr_url).text
    logger.info('public ip is {}'.format(ip))

    if ip:
        ip_cidr = '{}/32'.format(ip)
        return ip_cidr
