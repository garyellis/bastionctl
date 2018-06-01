from datetime import datetime, timedelta
from dateutil.tz import tzutc
import time
import botocore
import boto3
import logging
from ec2_patching.exceptions import StackDoesNotExistError

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
    creates the cloudformation stack
    """
    client = session.client('cloudformation')
    try:
        stack = client.create_stack(
            StackName=stack_name,
            TemplateBody=template_body
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

def get_stack_outputs(session, name):
    """
    Returns the outputs for the given cloudformation stack
    """
    client = session.client('cloudformation')
    stack_outputs = client.describe_stacks(StackName=name)['Stacks']
    if stack_outputs:
        return stack_outputs[0]['Outputs']

