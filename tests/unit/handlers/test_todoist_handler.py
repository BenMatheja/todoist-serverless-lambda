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
def todoist_event(event_file=TODOIST_EVENT):
    with open(event_file) as f:
        return json.load(f)


@pytest.fixture()
def context():
    return ''


def test_extract_user_agent(lambda_event):
    assert h.extract_useragent(lambda_event) == 'Todoist-Webhooks'


def test_extract_delivered_hmac(lambda_event):
    assert h.extract_delivered_hmac(lambda_event) == 'BTEp7cAire2IrbMCJCFJz28c1OpekswXDc8s7W51mY8='


def test_compute_hmac(todoist_event):
    h.compute_hmac(todoist_event, '9b65cf723f6d4824960bb9c74a24ebcd')


def test_handle_event(lambda_event, context):
    h.handle_event(lambda_event, context)
