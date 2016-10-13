import datetime
import re
import sys
import time
from collections import defaultdict

import click
import yaml
from slackclient import SlackClient

VERSION = (1, 0, 1)
__version__ = '1.0.1'


class Responder(object):

    def __init__(self, config):
        self.config = config
        self.client = SlackClient(config['token'])
        self.mapping = defaultdict(list)
        self.me = None

    def run(self):
        if self.client.rtm_connect():
            self.me = self.whoami(self.client.server.username)
            self.gather_channel_mapping()
            while True:
                self.process_messages(self.client.rtm_read())
                time.sleep(1)
        else:
            self._error("Connection failed. Is your token correct?")

    def process_messages(self, messages):
        for message in messages:
            if message.get('type') == 'message':
                ts = float(message['ts'])
                channel = message['channel']
                if message.get('subtype') == 'message_changed':
                    # there was an edit, so operate on the edited portion
                    text = message.get('message')['text']
                    user = message.get('message')['user']
                else:
                    text = message['text']
                    user = message['user']
                if channel not in self.mapping:
                    # Ignoring message in unmonitored channel
                    continue
                if abs(time.time() - ts) > 60:
                    # Ignoring old message
                    continue
                if user == self.me:
                    # Ignore messages sent by me
                    continue
                self.parse_message(text, channel)

    def parse_message(self, text, channel):
        rules = self.mapping[channel]
        for pattern, response in rules:
            matches = re.finditer(pattern, text)
            if matches:
                for match in matches:
                    replaced = match.expand(response)
                    self._log("Matched '{}' with pattern: '{}'. Responding: {}".format(
                        text, pattern, replaced
                    ))
                    self.respond(channel, replaced)
                continue

    def respond(self, channel, response):
        self.client.rtm_send_message(channel, response)

    def whoami(self, username):
        """
        Returns the ID for the provided `username`.
        """
        for user in self.client.server.users:
            if user == username:
                self._log("I am {} with id {}".format(username, user.id))
                return user.id
        self._error('Uh oh, couldn\'t determine bot user id from username: {}'.format(username))

    def gather_channel_mapping(self):
        """
        Stores {'room': [('regex', 'response')]} patterns. Channel names will
        be converted to appropriate channel IDs.
        """
        channels = self.client.server.channels
        channel_lookup = {channel.name: channel.id for channel in channels}
        for rule_name in self.config['rules']:
            rule = self.config['rules'][rule_name]
            rooms = rule.get('rooms')
            if rooms:
                for room in rooms:
                    actual_room = channel_lookup.get(room, room)
                    self.mapping[actual_room].append(
                        (re.compile(rule['pattern']), rule['response']))
            else:
                # monitor every channel
                for channel in channel_lookup.values():
                    self.mapping[channel].append(
                        (re.compile(rule['pattern']), rule['response']))

    def _log(self, message, level='DEBUG'):
        click.echo("{} - {} - {}".format(
            datetime.datetime.utcnow(), level, message
        ))

    def _error(self, message):
        click.secho("{} - {} - {}".format(
            datetime.datetime.utcnow(), 'ERROR', message
        ), fg='red')
        sys.exit(1)


@click.command()
@click.argument('config', type=click.File())
def cli(config):
    """
    Starts the responder bot with CONFIG yaml file defining a Slack
    `token` and `rules`.

    \b
    The most basic config file would contain a token and a single rule:
    \b
    token: 'your-bots-slack-token'
    rules:
      jira:
        pattern: '(?:^|[^\/])(\b[A-Z]{2,6}-\d{1,4}\b)(?:[^\/]|$)'
        response: 'http://domain.jira.com/jira/browse/\1'

    """
    parsed = yaml.safe_load(config)
    assert 'token' in parsed, "'token' does not exist in config file"
    assert 'rules' in parsed, "'rules' does not exist in config file"
    r = Responder(parsed)
    r.run()

if __name__ == '__main__':
    cli()
