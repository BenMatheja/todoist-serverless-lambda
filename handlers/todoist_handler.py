import json
import logging
import os
import base64
import hmac
import hashlib
import datetime
from pytz import timezone
from todoist_api_python.api import TodoistAPI

# ToDo: Migrate hour settings to configuration
WORKING_HOURS = 10
WORKING_MINUTES = 43
REQUIRED_WORKING_HOURS = 8
INTERMITTENT_FASTING_HOURS = 16


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


def compute_hmac(body, todoist_clientsecret=get_clientsecret()):

    # logger.info("compute_hmac with %s ", body)
    signature = base64.b64encode(hmac.new(
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
    # logger.info('ENVIRONMENT VARIABLES: %s', os.environ)
    logger.info('EVENT: %s', event)

    if event.get('body') and extract_useragent(event) == 'Todoist-Webhooks':
        logger.info('Request has body and useragent is correct')

        delivered_hmac = extract_delivered_hmac(event)
        computed_hmac = compute_hmac(event.get('body'))
        logger.info('Delivered hmac: ' + delivered_hmac)
        logger.info('Computed hmac: ' + computed_hmac)

        if computed_hmac == delivered_hmac:
            logger.info('Sent HMAC is valid with own computed one')
            json_body = json.loads(event.get('body'))
            if json_body.get('event_data')['content'] == "Kommen Zeit notieren":
                logger.info("Received a Clock-In Event")
                create_todoist_clockout_task()
                response = {"statusCode": "200",
                            "body": "clock-in event handled"
                            }
            if json_body.get('event_data')['content'] not in ["Kommen Zeit notieren",
                                                              "Last Meal finished"]:
                response = {"statusCode": "200",
                            "body": "generic event handled"
                            }
        else:
            response = {"statusCode": "403",
                        "body": "Unauthorized"
                        }
    else:
        response = {"statusCode": "400",
                    "body": "Bad Request"
                    }

    return response


"""
Routine to create a new Todoist Clock-Out Task using the Sync API
"""


def create_todoist_clockout_task():
    now = datetime.datetime.now().astimezone(timezone('Europe/Amsterdam'))
    soll = datetime.timedelta(hours=REQUIRED_WORKING_HOURS,
                              minutes=WORKING_MINUTES) + now
    acc = datetime.timedelta(hours=WORKING_HOURS, minutes=WORKING_MINUTES) + now
    clockin_time = str(now.hour) + ':' + str('%02d' % now.minute)
    clockout_time = str(acc.hour) + ':' + str('%02d' % acc.minute)
    soll_time = str(soll.hour) + ':' + str('%02d' % soll.minute)

    task_content = 'Gehen (Gekommen: ' + clockin_time + ', Soll erreicht: ' + soll_time + ')'

    logger.info('Create Todoist Clock-Out Task: ' + task_content + ' due at: ' + clockout_time)

    api = TodoistAPI(get_token())
    logger.info("Trying to connect to Todoist API with: %s", get_token())
    try:
        projects = api.get_projects()
        print(projects)
    except Exception as error:
        logger.warning('Todoist: API Sync failed' + error)
        exit()

    try:
        task = api.add_task(task_content,
                  project_id='178923234', date_string=clockout_time, labels=[2147513595],
                  priority=3)
        print(task)
        logger.info("Todoist Clock-Out Task has been created")
    except Exception as error:
        print(error)
