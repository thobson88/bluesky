"""
Demonstrates issue #1 - Send commands from client to server over TCP
"""

import os
import sys
import time


def client_test():
    """ Create a client, connect, send basic command """

    try:
        client = Client()

        client.connect(event_port=9000, stream_port=9001)

        print("Hello darkness...")
        client.send_event(b'TEST_EVENT', b'Hello darknesss...')

    except Exception as e:
        print(e)
        pass


def reset_test():
    """ Send the reset (IC IC) command """

    try:
        client = Client()
        client.connect(event_port=9000, stream_port=9001)

        # Send reset command
        client.send_event(b'STACKCMD', 'IC IC', target=b'*')

    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    rel = os.path.abspath(os.path.join(os.getcwd(), "../../"))
    sys.path.append(rel)

    from bluesky.network import Client

    client_test()
    time.sleep(5)

    print("Testing sim reset")
    reset_test()
