
# Notes

Scripts in this directory demonstrate basic interaction with BlueSky through it's Client class. This uses zmq (zero message queue) over TCP. The scripts must be run from this directory, and a BlueSky simulation / server must be running.

# Scripts

## `CommandTest.py`

Demonstrates issue #1 - Send commands from client to server over TCP.

`client_test` creates a client object and sends an event (named `TEST_EVENT`) to the server. The output can be viewed in the BlueSky server output. We can create custom events in this manner, which are handled by the server and don't interact with the simulation.

`reset_test` creates a client and sends a `STACKCMD` event, containing data `IC IC`. The `STACKCMD` event instructs the server to pass the data onto the simulation and evaluate it as a command. The `IC IC` command causes the simulation to reset to the start of the current scenario.

## `GetAircraftLoc.py`

Demonstrates issue #2 - Receive responses from the server over TCP.

Resets the simulation, creates an aircraft, then loops and continually requests the information for the created aircraft with the `POS <acid>` command.

Two-way communication is asynchronous and over different channels (`send_event` / `receive`). In the BlueSky `GuiClient` class, which is a subclass of the default Client, `receive` is hooked to the timeout event of a PyQt `QTimer` object. I believe this is how the gui clients poll for updates to the simulation.

## `ScenarioInteraction.py`

Demonstrates issue #8 - Interact with a simple scenario over TCP.

Loads the scenario data from `bluesky/turing/scenario/testControl.scn`. It then starts a thread which polls for the aircraft position, while the main thread sends a change altitude (`ALT 1000 FL105`) command instructing the aircraft to ascend.

There seems to be a delay between what the server emits and what is printed from the receiving thread. I believe this is due to a delay in reading from the event queue after sending the first few commands. This means that there are always a few messages waiting in the queue, even though we are reading at the same rate as commands are being sent.

## `CommandCli.py`

Useful script to either listen to server events, or send arbitrary commands.

# Misc. TODO

- Investigate the `GETSIMSTATE` command - seems to send back a large amount of information
- Investigate the use of the streaming interface
	- Can it be used to continually emit the simulation state?
	- Can we subscribe to events between the server and another client?
- Create a class / dependency diagram
- Investigate differences between the two versions of the simulations (qtgl / pygame), seems like there's a lot of code duplication