import botocore
import boto3
import logging

logger = logging.getLogger(__name__)

def import_keypair(session, name, public_key_material):
    """
    """
    client = session.client('ec2')
    public_key_material = public_key_material
    logger.info('import ssh key {} {}'.format(name, public_key_material))
    try:
        keypair = client.import_key_pair(
            KeyName=name,
            PublicKeyMaterial=public_key_material
        )
    except botocore.exceptions.ClientError as err:
        logger.error(err['Error']['Message'])
    
    return keypair['KeyName']

def delete_keypair(session, name):
    """
    """
    client = session.client('ec2')
    logger.info('deleting ssh keypair {}'.format(name))
    try:
        client.delete_key_pair(
            KeyName=name
        )
    except botocore.exceptions.ClientError as err:
        logger.error(err['Error']['Message'])


