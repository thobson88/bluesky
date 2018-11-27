"""
Tests for the BlueSky client base class.

Author <thobson@turing.ac.uk> Tim Hobson
"""

import pytest
import warnings
import time
import sys

import bluesky
from bluesky.network import Client, Server

EVENT_PORT = 9000
STREAM_PORT = 9001

@pytest.fixture(scope="session")
def server():
    try:
        # Start the server in headless mode.
        server = Server(True)
        server.start()
        print("Server started with host_id: {}".format(server.host_id))
    except Exception as e:
        print(e)
        sys.exit(1)
    return server


def shutdown_server(server):
    # Wait for the server thread to terminate.
    # Make sure there are no spawned_processes else this will hang.
    for n in server.spawned_processes:
        n.kill()
    server.join()


def get_client():
    try:
        client = Client()
        client.connect(event_port=EVENT_PORT, stream_port=STREAM_PORT)
    except Exception as e:
        print(e)
        sys.exit(1)
    return client


def test_send_event_quit(server):
    """ Send the 'QUIT' event"""

    try:
        target = get_client()
        assert server.running, "Server not running, but should be"

        target.send_event(b'QUIT')

        # Wait for the QUIT event to be processed.
        time.sleep(0.1)

        assert not server.running, "Server running, but shouldn't be"

    finally:
        shutdown_server(server)

# Suppress the DeprecationWarning, due to msgpack.unpackb(data, object_hook=decode_ndarray, encoding='utf-8') in client.py
@pytest.mark.filterwarnings("ignore:.*encoding is deprecated.*:DeprecationWarning")
def test_send_event_stackcmd(server):
    """ Send the 'STACKCMD' event"""

    try:
        target = get_client()

        # Initialise an attribute in the client instance to hold the textual data returned by the POS command.
        target.pos_text = ""

        # Reset the simulation
        target.send_event(b'STACKCMD', 'RESET', target=b'*')

        # Wait for the RESET event to be processed.
        # Omitting this line breaks the test; in that case the text response to the POS
        # command is constantly: "BlueSky Console Window: Enter HELP or ? for info."
        time.sleep(1)

        # Create an aircraft with a particular ID and altitude.
        aircraft_id = '1000'
        altitude = '17000'
        cre_command_data = 'CRE ' + aircraft_id + ' 0 0 0 0 ' + altitude + ' 500'
        target.send_event(b'STACKCMD', cre_command_data, target=b'*')

        assert target.sender_id == b'', "Client's sender_id differs from default (empty) value"
        assert not target.servers, "Client's servers dictionary should be empty, but isn't"

        # Define the POS command to poll for aircraft location.
        pos_command_data = 'POS ' + aircraft_id

        # Define a subscriber function to watch the client for 'ECHO' events in which the
        # payload contains a dictionary with a non-empty 'text' entry.
        def event_subscriber(name, data, sender_id):
            if name == b'ECHO':
                if isinstance(data, dict) and 'text' in data and data['text'] != '':
                    target.pos_text = data['text']

        target.event_received.connect(event_subscriber)

        target_string_pos = 'POS'
        done = False
        while not done:
            try:
                # Poll for aircraft location.
                target.send_event(b'STACKCMD', pos_command_data, target=b'*')
                target.receive()

                # This pause is not strictly necessary but avoids excessive polling before the server is ready.
                time.sleep(0.01)

                # Check that the Client's sender_id has been set to the Server's host_id (done in receive()).
                assert target.sender_id != b'', "Client's sender_id still has default (empty) value"

                # Check that the Client's servers dictionary is no longer empty.
                assert len(target.servers) == 1, "Client's servers dictionary should have one element"
                assert server.host_id in target.servers

                # Seek the target string in the textual data returned by the POS command.
                if (target.pos_text.find(target_string_pos) != -1):
                    # Print the full text to the console.
                    print("Target string found in POS response text:\n" + str(target.pos_text))
                    done = True

            except KeyboardInterrupt:
                sys.exit(0)

        assert done

        # Seek additional target strings in the response text: including the aircraft ID & altitude.
        target_string_id = 'Info on ' + aircraft_id
        target_string_altitude = 'Alt: ' + altitude + ' ft'

        assert target.pos_text.find(target_string_id) != -1
        assert target.pos_text.find(target_string_altitude) != -1

    finally:
        target.send_event(b'QUIT')
        shutdown_server(server)
