from slackclient._util import SearchDict


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
        self.users = SearchDict()
        self.users['123'] = User(self, 'botuser', '123')
        self.username = 'botuser'


class Channel(object):

    def __init__(self, idnum, name):
        self.id = idnum
        self.name = name


class User(object):

    def __init__(self, server, name, user_id):
        self.name = name
        self.server = server
        self.id = user_id
