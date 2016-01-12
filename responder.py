import re
import time
from collections import defaultdict

import click
import yaml
from slackclient import SlackClient


class Responder:

    def __init__(self, config):
        self.config = config
        self.client = SlackClient(config['token'])
        self.mapping = defaultdict(list)

    def run(self):
        if self.client.rtm_connect():
            self.gather_channel_mapping()
            print('mapping: ', self.mapping, sep='\n')
            while True:
                self.process_messages(self.client.rtm_read())
                time.sleep(1)
        else:
            print("Connection failed. Is your token correct?")

    def process_messages(self, messages):
        for message in messages:
            print("Message: {}".format(message))
            if message.get('type') == 'message':
                print('Processing Message: ', message, sep='\n')
                ts, text, channel = float(message['ts']), message['text'], message['channel']
                if channel not in self.mapping:
                    print('Ignoring message in unmonitored channel {}'.format(channel))
                    continue
                if abs(ts - time.time()) > 60:
                    print('Ignoring old message')
                    continue
                self.parse_message(text, channel)

    def parse_message(self, text, channel):
        rules = self.mapping[channel]
        for pattern, response in rules:
            match = re.search(pattern, text)
            if match:
                replaced = match.expand(response)
                self.respond(channel, replaced)
                break

    def respond(self, channel, response):
        print('Responding to {} with response: '.format(channel), response, sep='\n')
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
            print('rule: ', rule, sep='\n')
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
@click.option(
    '--config', '-c',
    type=click.File(),
    help='YAML configuration file location.')
def cli(config):
    parsed = yaml.safe_load(config)
    print("config: ", parsed, sep='\n')
    assert 'token' in parsed, "'token' does not exist in config file"
    assert 'team' in parsed, "'team' does not exist in config file"
    assert 'rules' in parsed, "'rules' does not exist in config file"
    r = Responder(parsed)
    r.run()

if __name__ == '__main__':
    cli()
