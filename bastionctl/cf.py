import bastionctl.config as config
from datetime import datetime, timedelta
from dateutil.tz import tzutc
import time
import botocore
import boto3
import logging
from bastionctl.exceptions import StackDoesNotExistError

logger = logging.getLogger(__name__)

class StackStatus(object):
    """
    Represents cloudformation stack statuses
    """
    PENDING = 'pending'
    IN_PROGRESS = 'in progress'
    COMPLETE = 'complete'
    FAILED = 'failed'


def get_stack_status(session, stack_name):
    """
    Returns the stack status
    """
    client = session.client('cloudformation')
    try:
        stack_status = client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
        logger.debug('stack status {} {}'.format(stack_name,stack_status))
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Message'].endswith('does not exist'):
            raise StackDoesNotExistError
        else:
            raise err

    return stack_status

def get_simple_stack_status(status):
    """
    Returns a simple stack status
    """
    simple_status = ''
    if status.endswith('_IN_PROGRESS'):
        simple_status = StackStatus.IN_PROGRESS
    elif status.endswith("_COMPLETE"):
        simple_status = StackStatus.COMPLETE
    elif status.endswith("_FAILED"):
        simple_status = StackStatus.FAILED

    logger.debug('simple stack status: {}'.format(status))
    return simple_status

def get_stack_events(session, stack_name):
    """
    Returns a dict of stack events
    """
    client = session.client('cloudformation')
    events = client.describe_stack_events(StackName=stack_name)['StackEvents']
    logger.debug('got events: {}'.format(events))
    return events

def get_recent_stack_events(events, last_event_datetime):
    """
    Returns a list of stack events since the last event datetime
    """
    recent_events = []
    if events:
        events.reverse()
        recent_events = [event for event in events if event['Timestamp'] > last_event_datetime]
    logger.debug('got recent events: {}'.format(recent_events))
    return recent_events

def log_stack_events(session, stack_name, last_event_datetime):
    """
    Logs stack events since the last event datetime and returns the last event datetime
    """
    stack_events = get_stack_events(session, stack_name)
    logger.debug('last event datetime: {}'.format(last_event_datetime))

    recent_stack_events = get_recent_stack_events(stack_events, last_event_datetime)
    if recent_stack_events:
        for event in recent_stack_events:
            logger.info("{} {} {} {} {} {}".format(
                event['Timestamp'].replace(microsecond=0).isoformat(),
            stack_name,
            event['LogicalResourceId'],
            event['ResourceType'],
            event['ResourceStatus'],
            event.get('ResourceStatusReason', '')
        ))
        last_event_datetime = event['Timestamp']
    return last_event_datetime

def wait_for_completion(session, stack_name):
    """
    Waits for the stack to complete
    """
    client = session.client('cloudformation')

    status = StackStatus.IN_PROGRESS

    last_event_datetime = (datetime.now(tzutc()) - timedelta(seconds=3))
    while status == StackStatus.IN_PROGRESS:
        try:
            status = get_simple_stack_status(get_stack_status(session, stack_name))
        except StackDoesNotExistError:
            raise StackDoesNotExistError

        last_event_datetime = log_stack_events(session, stack_name, last_event_datetime)
        time.sleep(4)
    return status

def create_stack(session, stack_name, template_body):
    """
    Creates the cloudformation stack
    """
    client = session.client('cloudformation')
    try:
        stack = client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Tags=[
                {'Key': config.cli_tag_key, 'Value': config.cli_tag_value },
                {'Key': '{}-version'.format(config.cli_tag_key), 'Value': config.cli_version }
            ]
        )
    except botocore.exceptions.ClientError as err:
        logger.error(err)
        exit(1)

    status = wait_for_completion(session, stack_name)
    if status != StackStatus.COMPLETE:
        logger.error('create stack failed with status: {}'.format(status))
        exit(1)

    logger.info('create stack complete')

def delete_stack(session, stack_name):
    """
    deletes the cloudformation stack
    """
    client = session.client('cloudformation')
    try:
        stack = client.delete_stack(
            StackName=stack_name
        )
    except:
        pass

    try:
        status = wait_for_completion(session, stack_name)
    except StackDoesNotExistError:
        logger.error('{} does not exist.'.format(stack_name)) 
        status = StackStatus.COMPLETE

    if status != StackStatus.COMPLETE:
        logger.error('delete stack failed.')
        exit(1)

    logger.info('delete stack complete.')

def validate_template(session, template_body):
    """
    Validates the cloudformation template
    """
    client = session.client('cloudformation')
    logger.info('validating template')
    try:
        client.validate_template(TemplateBody=template_body)
    except botocore.exceptions.ClientError as err:
        logger.error(err)
        exit(1)

    logger.info('validate template done')

def get_stack_outputs(session, name):
    """
    Returns the outputs for the given cloudformation stack
    """
    client = session.client('cloudformation')
    stack_outputs = client.describe_stacks(StackName=name)['Stacks']
    if stack_outputs:
        return stack_outputs[0]['Outputs']

def get_stack_output_value(outputs, output_key):
    """
    """
    value = [i['OutputValue'] for i in outputs if i['OutputKey'] == output_key]
    if value:
        return value[0]

def get_stacks(session):
    """
    Returns stacks created by this cli
    """
    tag_key = config.cli_tag_key
    tag_value = config.cli_tag_value
    stacks = []
    client = session.client('cloudformation')
    all_stacks = client.describe_stacks()['Stacks']
    for stack in all_stacks:
        tags = stack.get('Tags')
        if tags:
            for tag in tags:
                if tag['Key'] == tag_key and tag['Value'] == tag_value:
                    stacks.append(stack)
    return stacks

def get_stack_resources(session, name):
    """
    Returns the stack resources
    """
    client = session.client('cloudformation')
    stack_resources = client.list_stack_resources(StackName=name)['StackResourceSummaries']
    return stack_resources

def summarize_stack(session, name, stack_resources):
    """
    """
    client = session.client('cloudformation')
    stack_creation_time = client.describe_stacks(StackName=name)['Stacks'][0]['CreationTime']

    instance_type = 'AWS::EC2::Instance'
    sg_type = 'AWS::EC2::SecurityGroup'
    sg_ingress_type = 'AWS::EC2::SecurityGroupIngress'

    instance_id = [r['PhysicalResourceId'] for r in stack_resources if r['ResourceType'] == instance_type][0]
    sg_id = [r['PhysicalResourceId'] for r in stack_resources if r['ResourceType'] == sg_type][0]
    sg_ingress = [r['PhysicalResourceId'] for r in stack_resources if r['ResourceType'] == sg_ingress_type]

    private_ip_key = config.stack_output_private_ip_key
    public_ip_key = config.stack_output_public_ip_key
    vpc_id_key = config.stack_output_vpc_id_key

    stack_outputs = get_stack_outputs(session, name)
    public_ip = get_stack_output_value(stack_outputs, public_ip_key)
    private_ip = get_stack_output_value(stack_outputs, private_ip_key)
    vpc_id = get_stack_output_value(stack_outputs, vpc_id_key)

    summary = {
        'name': name,
        'instance_id': instance_id,
        'public_ip': public_ip,
        'private_ip': private_ip,
        'sg_id': sg_id,
        'sg_ingress_rules': len(sg_ingress),
        'stack_creation_time': stack_creation_time,
        'vpc_id': vpc_id
    }

    return summary

def get_stack_summaries(session):
    """
    """
    stack_summaries = []
    stacks = get_stacks(session)
    for stack in stacks:
        stack_name = stack['StackName']
        stack_resources = get_stack_resources(session, stack_name)
        stack_summary = summarize_stack(session, stack_name, stack_resources)
        stack_summaries.append(stack_summary)

    return stack_summaries
