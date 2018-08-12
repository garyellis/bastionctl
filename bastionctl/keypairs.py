import botocore
import boto3
from functools import wraps
from Crypto.PublicKey import RSA
import base64
import hashlib
import os
import logging

logger = logging.getLogger(__name__)

def import_keypair(session, name, public_key_material):
    """
    """
    client = session.client('ec2')
    public_key_material = public_key_material
    logger.info('importing keypair {} {}'.format(name, public_key_material))
    try:
        keypair = client.import_key_pair(
            KeyName=name,
            PublicKeyMaterial=public_key_material
        )
    except botocore.exceptions.ClientError as err:
        logger.error(err)
        keypair = {'KeyName': name}
    
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

def get_keypairs(session):
    """
    """
    client = session.client('ec2')
    keypairs = client.describe_key_pairs()['KeyPairs']
    return keypairs

def keypair_exists(session, name):
    """
    """
    keypairs = [i['KeyName'] for i in get_keypairs(session)]
    if name in keypairs:
        return True

def get_keypair_fingerprint(keypairs, name):
    """
    """
    fingerprint = [i.get('KeyFingerprint') for i in keypairs if i.get('KeyName') == name ]
    if fingerprint:
        return fingerprint[0]

def fingerprint(digest):
    """
    """
    return ':'.join(a+b for a,b in zip(digest[::2], digest[1::2]))

def get_prv_key_sha1_fingerprint(private_key):
    """
    """
    sha1digest = hashlib.sha1(private_key.exportKey('DER', pkcs=8)).hexdigest()
    sha1_fingerprint = fingerprint(sha1digest)
    return sha1_fingerprint

def get_pub_key_md5_fingerprint(private_key):
    """
    """
    public_key = RSA.importKey(private_key.exportKey('OpenSSH'))
    public_key_md5_digest = hashlib.md5(public_key.exportKey('DER')).hexdigest()
    md5_fingerprint = fingerprint(public_key_md5_digest)
    return md5_fingerprint

def get_key(private_key_file):
    """
    """
    key = None
    with open(private_key_file, 'r') as s:
        try:
            _key = RSA.importKey(s)
            if _key.has_private():
                key = _key
        except Exception as err:
            logger.debug('{}: is not an rsa private key'.format(private_key_file, err))
    return key

def get_key_fingerprints(private_key_file):
    """
    """
    key = None
    try:
        private_key = get_key(private_key_file)
        key = {
            'private_key_file': private_key_file,
            'private_key_file_private_sha1_fingerprint': get_prv_key_sha1_fingerprint(private_key),
            'private_key_file_public_md5_fingerprint': get_pub_key_md5_fingerprint(private_key)
        }
    except Exception as err:
        logger.debug('{}: {}'.format(private_key_file, err))
    return key

def get_ssh_keys_fingerprints(path):
    """
    """
    ssh_keys = []
    for root, dirs, files in os.walk(path):
        for name in files:
            ssh_key_fingerprints = get_key_fingerprints(os.path.join(root, name))
            if ssh_key_fingerprints:
                ssh_keys.append(ssh_key_fingerprints)
                logger.debug(ssh_key_fingerprints)
    return ssh_keys

def add_ssh_keys_fingerprints(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        records = f(*args, **kwargs)
        session = kwargs.get('session')
        ssh_keys_path = kwargs.get('path')
        aws_keypairs = get_keypairs(session)
        
        if ssh_keys_path:
            ssh_keys =  get_ssh_keys_fingerprints(ssh_keys_path)
            for i, row in enumerate(records):
                keypair_fingerprint = get_keypair_fingerprint(aws_keypairs, row.get('key_pair'))
                ssh_key_fingerprint = [
                    x for x in ssh_keys if keypair_fingerprint in [x['private_key_file_private_sha1_fingerprint'], x['private_key_file_public_md5_fingerprint']]
                ]
                if ssh_key_fingerprint:
                    records[i]['private_key_file'] = ssh_key_fingerprint[0]['private_key_file']
                    #records[i]['keypair_fingerprint'] = keypair_fingerprint
                    #records[i]['private_key_file_private_sha1_fingerprint'] = ssh_key_fingerprint[0]['private_key_file_private_sha1_fingerprint']
                    #records[i]['private_key_file_public_md5_fingerprint'] = ssh_key_fingerprint[0]['private_key_file_public_md5_fingerprint']
                    logger.debug('Found matching ssh key! {}'.format(records[i]))
        return records
    return wrapped
