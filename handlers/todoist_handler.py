import json
import logging
import os
import base64, hmac, hashlib
from todoist.api import TodoistAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_token():
    if os.getenv('TODOIST_APIKEY'):
        return os.getenv('TODOIST_APIKEY')
    else:
        return '3b3e61devtoken'


def get_clientsecret():
    if os.getenv('TODOIST_CLIENTSECRET'):
        return os.getenv('TODOIST_CLIENTSECRET')
    else:
        return '3b3e61devsecret'

"""
Routine to compute the X-Todoist-Hmac-SHA256	
To verify each webhook request was indeed sent by Todoist, 
an X-Todoist-Hmac-SHA256 header is included; 
it is a SHA256 Hmac generated using your client_secret as the encryption key 
and the whole request payload as the message to be encrypted. 
The resulting Hmac would be encoded in a base64 string.
"""


def compute_hmac(body, todoist_clientsecret = get_clientsecret()):
    message = bytes(json.dumps(body), 'utf-8')
    signature =  base64.b64encode(hmac.new(
        todoist_clientsecret.encode('utf-8'),
        message,
        digestmod=hashlib.sha256).digest()).decode('utf-8')
    logging.info('Computed hmac: %s', signature)
    return signature


def extract_useragent(event):
    return event.get('headers')['user-agent']


def extract_delivered_hmac(event):
    return event.get('headers')['X-Todoist-Hmac-SHA256']


"""
Handle the incoming Event
* Check Prerequisites (API-Key and Clientsecret present)
* Validate the Event (POST, Agent and contains Payload)
* Compute HMAC
* Work on Event
"""

def handle_event(event, context):
    todoist_apikey = get_token()
    todoist_clientsecret = get_clientsecret()

    if not todoist_apikey:
        logging.warning('Please set the todoist_apikey in environment variable.')
        exit()
    if not todoist_clientsecret:
        logging.warning('Please set the todoist_clientsecret in environment variable.')
        exit()

    # ToDo: POST should be covered via serverless service description
    if event.get('httpMethod') == 'POST' and event.get('body') and extract_useragent(event) == 'Todoist-Webhooks':
        logging.info('request was formally correct')
        # Compare sent hmac with own computed hmac
        delivered_hmac = extract_delivered_hmac(event)
        computed_hmac = compute_hmac(event.get('body'))
        logging.info('Delivered hmac: %s ', delivered_hmac)
        logging.info('Conputed hmac: %s', computed_hmac)

        if computed_hmac == delivered_hmac:
            logging.info('Sent HMAC is valid with own computed one')
            json_body = json.loads(event.get('body'))
            if json_body.get('event_data')['content'] == "Kommen Zeit notieren":
                logging.info("Received a Clock-In Event")
                # Create Todoist Task









def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
