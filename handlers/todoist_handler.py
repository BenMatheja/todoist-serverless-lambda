import json
import logging
import os
import base64, hmac, hashlib, http.client
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
    #logger.info("compute_hmac with %s ", body)
    signature =  base64.b64encode(hmac.new(
        todoist_clientsecret.encode('utf-8'),
        body.encode('utf-8'),
        digestmod=hashlib.sha256).digest()).decode('utf-8')
    return signature


def extract_useragent(event):
    return event.get('headers')['User-Agent']

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
    #logger.info('ENVIRONMENT VARIABLES: %s', os.environ)
    logger.info('EVENT: %s', event)

    todoist_clientsecret = get_clientsecret()
    if not todoist_clientsecret:
        logger.error('Please set the todoist_clientsecret in environment variable.')
        exit()

    if  event.get('body') and extract_useragent(event) == 'Todoist-Webhooks':
        #logger.info('Request has body and useragent is correct')

        delivered_hmac = extract_delivered_hmac(event)
        computed_hmac = compute_hmac(event.get('body'))
        logger.info('Delivered hmac: ' + delivered_hmac)
        logger.info('Computed hmac: ' + computed_hmac)

        if computed_hmac == delivered_hmac:
            logger.info('Sent HMAC is valid with own computed one')
            json_body = json.loads(event.get('body'))
            if json_body.get('event_data')['content'] == "Kommen Zeit notieren":
                logger.info("Received a Clock-In Event")
                create_todoist_task()
                response =  {"status": http.client.responses[http.client.CREATED]}
            else:
                response =  {"status": http.client.responses[http.client.NO_CONTENT]}
        else:
           response = {"status": http.client.responses[http.client.UNAUTHORIZED]} 
    else:
        response = {"status": http.client.responses[http.client.BAD_REQUEST]}
    
    return response


"""
Routine to create a new Todoist Task using the Sync API
"""
def create_todoist_task():
    now = datetime.datetime.now().astimezone(timezone('Europe/Amsterdam'))
    soll = datetime.timedelta(hours=REQUIRED_WORKING_HOURS, minutes=WORKING_MINUTES) + now
    acc = datetime.timedelta(hours=WORKING_HOURS, minutes=WORKING_MINUTES) + now
    clockin_time = str(now.hour) + ':' + str('%02d' % now.minute)
    clockout_time = str(acc.hour) + ':' + str('%02d' % acc.minute)
    soll_time = str(soll.hour) + ':' + str('%02d' % soll.minute)

    logger.info('Create Todoist Task: ' + 'Gehen (Gekommen: ' + clockin_time + ', Soll erreicht: ' + soll_time + ' ) due at ' + clockout_time)

    api = TodoistAPI(token=get_token(), cache="/tmp/todoist")
    logger.info("Trying to connect to Todoist API with: %s", get_token())
    if not api.sync():
        logger.warning('Todoist: API Sync failed')
        exit()

    api.items.add('Gehen (Gekommen: ' + clockin_time + ', Soll erreicht: ' + soll_time + ' )',
                  project_id='178923234', date_string=clockout_time, labels=[2147513595],
                  priority=3)
    if api.commit():
        logger.info("Todoist Task has been created")
