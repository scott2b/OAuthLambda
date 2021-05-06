import json
import logging
import os
import sys
import traceback
import src.endpoints


logger = logging.getLogger()
logger.setLevel(logging.INFO)

CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(CWD, 'src'))


def handler(f):
    """https://towardsdatascience.com/why-you-should-never-ever-print-in-a-lambda-function-f997d684a705"""
    def wrapper(event, context):
        try:
            logger.info(f'event: {event}')
            return f(event, context)
        except Exception as exp:
            exception_type, exception_value, exception_traceback = sys.exc_info()
            traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
            err_msg = json.dumps({
                "errorType": exception_type.__name__,
                "errorMessage": str(exception_value),
                "stackTrace": traceback_string
            })
            logger.error(err_msg)
    return wrapper


@handler
def hello(event, context):
    """Authentication required."""
    return src.endpoints.hello(event, context)


@handler
def token(event, context):
    return src.endpoints.token(event, context)


@handler
def refresh_token(event, context):
    return src.endpoints.refresh_token(event, context)
