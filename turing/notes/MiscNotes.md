
# Misc. BlueSky Notes

## Startup Modes

TODO

## Networking Module

BS seems to implement a full client/server model, which supports (amongst who knows what else):

- Multiple simulations running per server
- Some sort of streaming connection (?)
- Complex routing of messages through multiple connected servers (?)

Messages are sent between nodes using the `zmq` message queueing library ([site](http://zeromq.org/)), which marshals the message data over TCP sockets. Python objects (including `numpy` arrays) are serialized using `msgpack` ([site](https://msgpack.org/index.html)), which seems to be an alternative format to JSON.

`zmq` seems to support both publish-subscribe as well as polling patterns. BlueSky implements connections using both these methods:

- Event connections: Uses the polling method; you manually check for any messages in the queue
- Stream connections: Use pub-sub to somehow react to messages as soon as they are received

Currently unclear how the stream messages are handled, or if they are used at all.

Some of the object naming doesn't appear well thought out - multiple uses of the terms `node`, `route`, and `event` can be seen, not even including any clashes with their use in the actual simulation code. Eugh.

### Server.py

Subclass of `Threading.Thread`.

Useful fields:

- `scenarios`: Array of scenarios, something to do with the `BATCH` command (?)
- `clients`: Array of connected clients
- `workers`: Array of spawned workers (simulations)

Useful methods:

- `sendScenario(worker_id)`: Send a scenario from `self.scenarios` to the target worker
- `addnodes(count=1)`: Add a worker sim. Actually just creates a subprocess and calls `BlueSky.py --sim`. Called by `run()`, so there is always a sim started when you run a `Server` object
- `run()`: Main server loop when started as a thread. Sets up the various messaging bits then handles events in a loop until `self.running` unset

### Client.py

Base class for interacting with a server object.

Useful fields:

Useful methods:

- `send_event(name, data=None, target=None)`: Sends an event. Target can be set to broadcast to all nodes.
- `receive(timeout=0)`: Checks for any received messages (via either event or stream), and passes them on to the appropriate handle functions

### Node.py
"Encapsulates the sim process, and manages process I/O". The (qtgl) simulation subclasses this and overrides the `step()` and `event(eventname, eventdata, sender_id)`  methods to run the simulation and interact with the server

## Simulation Module

TODO: Command stack

### PyGame
### QtGl

## Traffic Module