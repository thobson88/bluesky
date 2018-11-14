"""
Tests for the BlueSky client base class.

Author <thobson@turing.ac.uk> Tim Hobson
"""

import pytest
import time

import bluesky
from bluesky.network import Client, Server

EVENT_PORT = 9000
STREAM_PORT = 9001

def get_server():
    server = Server(True)
    server.start()
    return server

def get_client():
    client = Client()
    client.connect(event_port=EVENT_PORT, stream_port=STREAM_PORT)
    return client

def test_send_event():
    """ Send the send_event command"""

    server = get_server()
    try:
        target = get_client()

        assert server.running, "Server not running, but should be"

        target.send_event(b'QUIT')

        # Wait for the QUIT event to be processed.
        time.sleep(0.1)

        assert not server.running, "Server running, but shouldn't be"

    finally:
        # Wait for the server thread to terminate.
        # Make sure there are no spawned_processes else this will hang.
        for n in server.spawned_processes:
            n.kill()
        server.join()
