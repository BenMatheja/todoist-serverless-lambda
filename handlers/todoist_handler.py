import json
import logging
import os
import base64, hmac, hashlib
import datetime
from pytz import timezone
from todoist.api import TodoistAPI
# ToDo: Migrate hour settings to configuration
WORKING_HOURS = 10
WORKING_MINUTES = 43
REQUIRED_WORKING_HOURS = 8

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
    return event.get('headers')['x-todoist-hmac-sha256']


"""
Handle the incoming Event
* Check Prerequisites (API-Key and Clientsecret present)
* Validate the Event (POST, Agent and contains Payload)
* Compute HMAC
* Work on Event
"""
def handle_event(event, context):
    todoist_clientsecret = get_clientsecret()
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
                create_todoist_task()
    response = {
        "statusCode": 200,
        "body": ""
    }
    return response


"""
Routine to create a new Todoist Task using the Sync API
"""
def create_todoist_task():
    todoist_apikey = get_token()
    if not todoist_apikey:
        logging.warning('Please set the todoist_apikey in environment variable.')
        exit()

    now = datetime.datetime.now().astimezone(timezone('Europe/Amsterdam'))
    soll = datetime.timedelta(hours=REQUIRED_WORKING_HOURS, minutes=WORKING_MINUTES) + now
    acc = datetime.timedelta(hours=WORKING_HOURS, minutes=WORKING_MINUTES) + now
    clockin_time = str(now.hour) + ':' + str('%02d' % now.minute)
    clockout_time = str(acc.hour) + ':' + str('%02d' % acc.minute)
    soll_time = str(soll.hour) + ':' + str('%02d' % soll.minute)

    logging.info('Create Todoist Task: ' + 'Gehen (Gekommen: ' + clockin_time + ', Soll erreicht: ' + soll_time + ' ) due at ' + clockout_time)

    api = TodoistAPI(token=get_token(), cache="/tmp/todoist")
    if not api.sync():
        logging.warning('Connecting to Todoist failed')
        exit()

    api.items.add('Gehen (Gekommen: ' + clockin_time + ', Soll erreicht: ' + soll_time + ' )',
                  project_id='178923234', date_string=clockout_time, labels=[2147513595],
                  priority=3)

    if not api.commit():
        logging.warning('Delivering the new Task to Todoist failed')




