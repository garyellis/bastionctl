import logging
import logging.config

def setup_logging(log_level):
    """
    """
#    logging.config.dictConfig({
#        'version': 1,
#        'disable_existing_loggers': False,
#    })

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
