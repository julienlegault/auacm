from tornado.websocket import WebSocketHandler
from json import loads
from time import time

def make_flasknado():
    """ Creates a new class instance of Flasknado

    In a sense, this is kind of a hack. The problem is that the way Tornado
    works, it requires sending a WebSocketHandler class rather than an instance
    of that class. This means that in order to have separate instances, we must
    dynamically create different classes at runtime. This function simply
    returns a Flasknado class with an empty set of clients.
    """

    values = dict(Flasknado.__dict__)
    values['clients'] = []  # give the new instance a new set of clients
    return type('Flasknado', Flasknado.__bases__, values)

class Flasknado(WebSocketHandler):
    """ A class for handling sockets

    This class acts as a singleton that contains all of the websocket clients
    that are currently connected to the server.
    """

    clients = []  # initialize the list of clients to an empty list

    @classmethod
    def wrap(self, event_type, data):
        return {
            'eventType': event_type,
            'data': data
        }

    @classmethod
    def emit(self, event_type, data):
        for client in self.clients:
            client.write_message(self.wrap(event_type, data))

    def open(self):
        Flasknado.clients.append(self)

    def on_close(self):
        Flasknado.clients.remove(self)

    def on_message(self, message):
        data = loads(message)
        if data['eventType'] == 'system_time':
            self.write_message(self.wrap('system_time', {
                'milliseconds': int(time() * 1000)
            }))

    def data_received(self, data):
        pass
