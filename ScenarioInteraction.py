"""
Example script for issue #8
"""

import os
import sys
import threading
import time

import msgpack
import zmq

from bluesky.network import Client
from bluesky.network.common import get_hexid
from bluesky.network.npcodec import decode_ndarray


# Subclass of the BlueSky network client object
class TestClient(Client):

    def __init__(self):
        super(TestClient, self).__init__()

    def receive(self, timeout=0):
        try:
            socks = dict(self.poller.poll(timeout))
            if socks.get(self.event_io) == zmq.POLLIN:

                msg = self.event_io.recv_multipart()

                # Remove send-to-all flag if present
                if msg[0] == b'*':
                    msg.pop(0)

                route, eventname, data = msg[:-2], msg[-2], msg[-1]

                self.sender_id = route[0]
                route.reverse()
                pydata = msgpack.unpackb(data, object_hook=decode_ndarray, encoding='utf-8')

                # Print the data, filtering out unwanted messages
                if isinstance(pydata, dict) and \
                        'text' in pydata and \
                        pydata['text'] != '':
                    print('\n' + pydata['text'])

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
        print('Client created (ID: {})'.format(get_hexid(client.client_id)))

        # 9000 seems to be the default server event port, not sure about the use of the stream_port
        client.connect(event_port=9000, stream_port=9001)
    except Exception as e:
        print(e)
        sys.exit(1)
    return client


class ReceiveThread(threading.Thread):
    def __init__(self, client, data):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.client = client
        self.data = data

    def run(self):
        while not self.event.is_set():
            self.client.send_event(b'STACKCMD', data, target=b'*')
            self.client.receive()
            time.sleep(1)

        print('Thread exit')


if __name__ == "__main__":

    # Only works for files relative to the repo. root for now
    scnFile = r'scenario\KLM1705-EHAM-LEMD.scn'

    # Aircraft ID for the above scenario, will need updated if you choose a different scenario
    acid = 'KLM1705'

    filePath = os.path.join(os.getcwd(), scnFile)

    if not os.path.isfile(filePath):
        print('Could not fine scenario file ' + filePath)
        sys.exit(1)

    client = get_client()

    # Create a thread which will continually poll for the aircraft information
    data = 'POS ' + acid
    thread = ReceiveThread(client, data)

    print('Sending sim reset')
    client.send_event(b'STACKCMD', 'RESET', target=b'*')

    time.sleep(1)

    print('Calling IC {}'.format(filePath))
    client.send_event(b'STACKCMD', 'IC {}'.format(filePath), target=b'*')

    time.sleep(1)

    print('FF for 5s')
    client.send_event(b'STACKCMD', 'FF', target=b'*')
    time.sleep(5)
    client.send_event(b'STACKCMD', 'OP', target=b'*')

    # Start the receive thread
    thread.start()

    time.sleep(5)

    # Send a command
    cmd = 'ALT {} FL170'.format(acid)
    print(cmd)
    client.send_event(b'STACKCMD', cmd, target=b'*')

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            thread.event.set()
            sys.exit(0)
