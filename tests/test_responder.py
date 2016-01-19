import slack_responder

import pytest
from mocks import SlackClient

config = {
    'token': 'my-token',
    'rules': {
        'jira': {
            # pattern: ABCD-1234 without any surrounding slashes / /
            'pattern': r'(?<!/)\b([A-Z]{2,6}-\d{1,4})\b(?!/)',
            'response': r'https://domain.jira.com/browse/\1'
        }
    }
}


@pytest.fixture(autouse=True)
def mock_slack_client(monkeypatch):
    monkeypatch.setattr(slack_responder, 'SlackClient', SlackClient)


def test_single_pattern():
    r = slack_responder.Responder(config)
    assert r.client.rtm_connect(), "Could not connect"
    r.gather_channel_mapping()
    r.parse_message('ABC-123', r.client.server.channels[0].id)
    assert len(r.client.sent) == 1
    assert r.client.sent[0][1] == 'https://domain.jira.com/browse/ABC-123'
    r.client.sent = []
    r.parse_message('Im working on ABC-123 now', r.client.server.channels[0].id)
    assert len(r.client.sent) == 1
    assert r.client.sent[0][1] == 'https://domain.jira.com/browse/ABC-123'
    r.client.sent = []
    r.parse_message('/ABC-123', r.client.server.channels[0].id)
    assert len(r.client.sent) == 0
    r.client.sent = []
    r.parse_message('/ABC-123/', r.client.server.channels[0].id)
    assert len(r.client.sent) == 0
    r.client.sent = []


def test_multiple_patterns():
    r = slack_responder.Responder(config)
    assert r.client.rtm_connect(), "Could not connect"
    r.gather_channel_mapping()
    r.parse_message('Ticket1: ABC-123 Ticket2: ABC-321', r.client.server.channels[0].id)
    assert len(r.client.sent) == 2
    assert r.client.sent[0][1] == 'https://domain.jira.com/browse/ABC-123'
    assert r.client.sent[1][1] == 'https://domain.jira.com/browse/ABC-321'


def test_mutliple_patterns_next_to_each_other():
    r = slack_responder.Responder(config)
    assert r.client.rtm_connect(), "Could not connect"
    r.gather_channel_mapping()
    r.parse_message('Tickets: ABC-123 ABC-321', r.client.server.channels[0].id)
    assert len(r.client.sent) == 2
    print(r.client.sent[0])
    assert r.client.sent[0][1] == 'https://domain.jira.com/browse/ABC-123'
    assert r.client.sent[1][1] == 'https://domain.jira.com/browse/ABC-321'
