import sys
import threading
import time

import msgpack
import zmq

from bluesky.network.client import Client
from bluesky.network.npcodec import decode_ndarray


class TestClient(Client):

    def __init__(self):
        super(TestClient, self).__init__()

    def receive(self, timeout=0):
        try:
            socks = dict(self.poller.poll(timeout))
            if socks.get(self.event_io) == zmq.POLLIN:

                msg = self.event_io.recv_multipart()
                print("Event msg: {}".format(msg))

                # Remove send-to-all flag if present
                if msg[0] == b'*':
                    msg.pop(0)

                route, eventname, data = msg[:-2], msg[-2], msg[-1]

                self.sender_id = route[0]
                route.reverse()
                pydata = msgpack.unpackb(data, object_hook=decode_ndarray, encoding='utf-8')
                if eventname == b'NODESCHANGED':
                    self.servers.update(pydata)
                    self.nodes_changed.emit(pydata)

                    # If this is the first known node, select it as active node
                    nodes_myserver = next(iter(pydata.values())).get('nodes')
                    if not self.act and nodes_myserver:
                        self.actnode(nodes_myserver[0])
                elif eventname == b'QUIT':
                    self.signal_quit.emit()
                else:
                    self.event(eventname, pydata, self.sender_id)

            if socks.get(self.stream_in) == zmq.POLLIN:
                msg = self.stream_in.recv_multipart()

                print("Stream msg: {}".format(msg))

                strmname = msg[0][:-5]
                sender_id = msg[0][-5:]
                pydata = msgpack.unpackb(msg[1], object_hook=decode_ndarray, encoding='utf-8')
                self.stream(strmname, pydata, sender_id)

            # If we are in discovery mode, parse this message
            if self.discovery and socks.get(self.discovery.handle.fileno()):
                dmsg = self.discovery.recv_reqreply()
                if dmsg.conn_id != self.client_id and dmsg.is_server:
                    self.server_discovered.emit(dmsg.conn_ip, dmsg.ports)

        except zmq.ZMQError:
            return False


def get_client():
    try:
        client = TestClient()
        client.connect(event_port=9000, stream_port=9001)
    except Exception as e:
        print(e)
        sys.exit(1)
    return client


class ReceiveThread(threading.Thread):
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.func = func

    def run(self):
        while not self.event.is_set():
            self.func()

        print('Thread exit')


if __name__ == '__main__':

    print("BlueSky command CLI")

    client = get_client()
    thread = ReceiveThread(client.receive)

    mode = input('Choose mode (\'listen\' or \'command\') > ')

    if mode == 'listen' or mode == 'l':

        print('Starting listen thread...')

        thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)
        finally:
            thread.event.set()

    elif mode == 'command' or mode == 'c':

        print('Command mode, enter inputs')

        try:
            while True:
                cmd = input('> ')
                if cmd != '':
                    client.send_event(b'STACKCMD', cmd, target=b'*')
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
        finally:
            thread.event.set()
    else:
        print('Unknown mode {}'.format(mode))
