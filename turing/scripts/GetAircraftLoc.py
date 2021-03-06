"""
Demonstrates issue #2 - Receive responses from the server over TCP.

Resets the sim, creates an aircraft, then continually polls for its position.
"""

import os
import sys
import time

import msgpack
import zmq


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


if __name__ == "__main__":

    rel = os.path.abspath(os.path.join(os.getcwd(), "../../"))
    sys.path.append(rel)

    from bluesky.network import Client
    from bluesky.network.common import get_hexid
    from bluesky.network.npcodec import decode_ndarray


    class TestClient(Client):
        """ Simple subclass of the BlueSky Client class. Only really used so we can print
        out the data from any received events """

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
                        print(pydata['text'])

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


    client = get_client()

    print('Resetting sim')
    client.send_event(b'STACKCMD', 'RESET', target=b'*')

    time.sleep(0.5)

    print("Creating aircraft")
    data = 'CRE 1000 0 0 0 0 17000 500'
    client.send_event(b'STACKCMD', data, target=b'*')

    print('Polling for location...')
    data = 'POS 1000'

    while True:
        try:
            client.send_event(b'STACKCMD', data, target=b'*')
            client.receive()
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)
