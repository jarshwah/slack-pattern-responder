import re
import sys
import time
from collections import defaultdict

import click
import yaml
from slackclient import SlackClient

VERSION = (0, 1, 2)
__version__ = '0.1.2'


class Responder(object):

    def __init__(self, config):
        self.config = config
        self.client = SlackClient(config['token'])
        self.mapping = defaultdict(list)

    def run(self):
        if self.client.rtm_connect():
            self.gather_channel_mapping()
            while True:
                self.process_messages(self.client.rtm_read())
                time.sleep(1)
        else:
            print("Connection failed. Is your token correct?")
            sys.exit(1)

    def process_messages(self, messages):
        for message in messages:
            if message.get('type') == 'message':
                ts, text, channel = float(message['ts']), message['text'], message['channel']
                if channel not in self.mapping:
                    # Ignoring message in unmonitored channel
                    continue
                if abs(ts - time.time()) > 60:
                    # Ignoring old message
                    continue
                self.parse_message(text, channel)

    def parse_message(self, text, channel):
        rules = self.mapping[channel]
        for pattern, response in rules:
            matches = re.finditer(pattern, text)
            if matches:
                for match in matches:
                    replaced = match.expand(response)
                    if re.search(pattern, replaced):
                        self.respond(
                            channel, "Your rules will cause infinite loops, fix them! {}".format(pattern))
                        break
                    self.respond(channel, replaced)
                break

    def respond(self, channel, response):
        self.client.rtm_send_message(channel, response)

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
