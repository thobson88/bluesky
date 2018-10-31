#!/usr/bin/env python

from __future__ import print_function

def tcpTest():

    from bluesky.tools.network import StackTelnetServer
    import socket

    TCP_HOST = '127.0.0.1'
    TCP_PORT = 9000

    #telnet_in = StackTelnetServer()

    sock = socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TCP_HOST, TCP_PORT))

    # sock.send()???

    sock.close()

    # parent_pid = os.getpid()
    # parent = psutil.Process(parent_pid)
    # child = parent.children(recursive=False)[0]
    # child.send_signal(signal.SIGKILL)


def eventImpl(self, name, data, sender_id):
    print("Event!")


def clientTest():

    from bluesky.network.client import Client

    try:
        client = Client()
        client.event = eventImpl

        client.connect(event_port=9000, stream_port=9001)

        print("Hello darkness...")
        client.send_event(b'CMD', b'Hello darknesss...')

    except Exception as e:
        print(e)
        pass


def resetTest():

    from bluesky.network.client import Client

    try:
        client = Client()
        client.event = eventImpl
        client.connect(event_port=9000, stream_port=9001)

        # Send reset command
        client.send_event(b'STACKCMD', 'IC IC', target=b'*')

    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':

    #tcpTest()
    #clientTest()
    resetTest()
