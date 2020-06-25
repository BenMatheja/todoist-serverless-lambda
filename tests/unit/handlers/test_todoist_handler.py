import json
import os
import pytest

import handlers.todoist_handler as h

LAMBDA_EVENT = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'events',
    'lambda-event.json'
)

LAMBDA_EVENT_BODY = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'events',
    'lambda-event-body.json'
)

LAMBDA_EVENT_BODY_EXTENDED = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'events',
    'lambda-event-body-extended.json'
)

TODOIST_EATING_EVENT = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'events',
    'todoist-eating-event.json'
)

TODOIST_EVENT = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'events',
    'todoist-event.json'
)


@pytest.fixture()
def lambda_event(event_file=LAMBDA_EVENT):
    with open(event_file) as f:
        return json.load(f)

@pytest.fixture()
def lambda_event_body(event_file=LAMBDA_EVENT_BODY):
    with open(event_file) as f:
        return json.load(f)

@pytest.fixture()
def lambda_event_body_extended(event_file=LAMBDA_EVENT_BODY_EXTENDED):
    with open(event_file) as f:
        return json.load(f)

@pytest.fixture()
def todoist_event(event_file=TODOIST_EVENT):
    with open(event_file) as f:
        return json.load(f)

@pytest.fixture()
def todoist_eating_event(event_file=TODOIST_EATING_EVENT):
    with open(event_file) as f:
        return json.load(f)

@pytest.fixture()
def context():
    return ''

'''
Functional Tests
'''


def test_extract_user_agent(lambda_event):
    assert h.extract_useragent(lambda_event) == 'Todoist-Webhooks'


def test_extract_delivered_hmac(lambda_event):
    assert h.extract_delivered_hmac(lambda_event) == '110FA32syjKn2ZclljQp2qscyH+Hcd9t0KzHaVqvhDY='


def test_compute_hmac(todoist_event):
    assert h.compute_hmac(json.dumps(todoist_event), '9b65cf723f6d4824960bb9c74a24ebcd') == 'b+YoFmRYu8pd7fLhsEmtDXBToWXIGqYOvRNDLcK+Yy8='

def test_handle_lambda_event_with_no_body(lambda_event, context):
    response = h.handle_event(lambda_event, context)
    assert response["status"] == "Bad Request"

def test_handle_lambda_event_with_malformed_body(lambda_event_body, context):
    response = h.handle_event(lambda_event_body, context)
    assert response["status"] == "Unauthorized"

def test_handle_lambda_event_with_extended_body(lambda_event_body_extended, context):
    response = h.handle_event(lambda_event_body_extended, context)
    assert response["status"] == "Bad Request"
    
def test_create_todoist_task():
  h.create_todoist_task()