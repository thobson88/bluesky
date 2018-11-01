#!/usr/bin/env python

from __future__ import print_function

from bluesky.network.client import Client
import time

def client_test():
    ''' Create a client, connect, send basic command '''

    try:
        client = Client()

        client.connect(event_port=9000, stream_port=9001)

        print("Hello darkness...")
        client.send_event(b'CMD', b'Hello darknesss...')

    except Exception as e:
        print(e)
        pass


def reset_test():
    ''' Send the reset (IC IC) command '''

    try:
        client = Client()
        client.connect(event_port=9000, stream_port=9001)

        # Send reset command
        client.send_event(b'STACKCMD', 'IC IC', target=b'*')

    except Exception as e:
        print(e)
        pass


def recv_test():
    ''' Test we can receive some data from server -> client '''

    try:
        client = Client()
        client.connect(event_port=9000, stream_port=9001)

        # TODO:
        #client.subscribe(b'ECHO')
        #client.send_event(b'ECHO', 'Hello there!', target=b'*')

    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':

    #client_test()
    reset_test()
    #recv_test()
