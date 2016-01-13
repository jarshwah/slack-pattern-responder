class SlackClient(object):

    def __init__(self, token):
        self.token = token
        self.server = Server()
        self.sent = []

    def rtm_connect(self):
        return True

    def rtm_send_message(self, channel, response):
        self.sent.append((channel, response))


class Server(object):

    def __init__(self):
        self.channels = [
            Channel('123', 'general'),
            Channel('321', 'random')
        ]


class Channel(object):

    def __init__(self, idnum, name):
        self.id = idnum
        self.name = name
