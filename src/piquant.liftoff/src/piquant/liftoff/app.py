import tornado
from tornado import websocket
import pika
from pika.adapters.tornado_connection import TornadoConnection
import os


class PikaClient(object):

    def __init__(self, io_loop):
        pika.log.info('PikaClient: __init__')
        self.io_loop = io_loop

        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None

        self.event_listeners = set([])

    def connect(self):
        if self.connecting:
            pika.log.info('PikaClient: Already connecting to RabbitMQ')
            return

        pika.log.info('PikaClient: Connecting to RabbitMQ')
        self.connecting = True

        cred = pika.PlainCredentials('guest', 'guest')
        param = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            virtual_host='/',
            credentials=cred
        )

        self.connection = TornadoConnection(param,
            on_open_callback=self.on_connected)
        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        pika.log.info('PikaClient: connected to RabbitMQ')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        pika.log.info('PikaClient: Channel open, Declaring exchange')
        self.channel = channel
        # declare exchanges, which in turn, declare
        # queues, and bind exchange to queues

    def on_closed(self, connection):
        pika.log.info('PikaClient: rabbit connection closed')
        self.io_loop.stop()

    def on_message(self, channel, method, header, body):
        pika.log.info('PikaClient: message received: %s' % body)
        self.notify_listeners(event_factory(body))

    def notify_listeners(self, event_obj):
        # here we assume the message the sourcing app
        # post to the message queue is in JSON format
        event_json = json.dumps(event_obj)

        for listener in self.event_listeners:
            listener.write_message(event_json)
            pika.log.info('PikaClient: notified %s' % repr(listener))

    def add_event_listener(self, listener):
        self.event_listeners.add(listener)
        pika.log.info('PikaClient: listener %s added' % repr(listener))

    def remove_event_listener(self, listener):
        try:
            self.event_listeners.remove(listener)
            pika.log.info('PikaClient: listener %s removed' % repr(listener))
        except KeyError:
            pass

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect('/static/boot', permanent=True)

class MyWebSocketHandler(websocket.WebSocketHandler):
    def open(self, *args, **kwargs):
        self.application.pc.add_event_listener(self)
        pika.log.info("WebSocket opened")
    def on_close(self):
        pika.log.info("WebSocket closed")
        self.application.pc.remove_event_listener(self)


settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "mmsp97gwjshdwjwndis9ujdjshsdudjshdkskdjshsdi",
    "login_url": "/login",
    "xsrf_cookies": True,
}

handlers = [
    (r'/ws', MyWebSocketHandler),
    (r'/', MainHandler),
    (r'/static/(.*)', tornado.web.StaticFileHandler,
     dict(path=settings['static_path'])),
    ]

application = tornado.web.Application(handlers,**settings)


def main():
    pika.log.setup(color=True)
    io_loop = tornado.ioloop.IOLoop.instance()
    # PikaClient is our rabbitmq consumer
    pc = PikaClient(io_loop)
    application.pc = pc
    application.pc.connect()
    application.listen(8888)
    io_loop.start()

if __name__ == '__main__':
    main()
