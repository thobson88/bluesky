# Notes on the startup sequence

### `BlueSky.py`

Main entry point. Imports `main` from `BlueSky_qtgl` (if using the Qt version),
then checks whether this module is main and calls `main()` if so.

### `BlueSky_qtgl.py`

Main entry for the Qt version. Imports `bluesky`, among others. Sets up some
exception handling to "counter" some PyQt problem.

Calls `bluesky.init()`.

Then decides if we're in GUI mode or "sim" mode (whatever that means) based on
whether `bluesky.settings.is_gui` is true, and, if not, whether
`bluesky.settings.si_sim` is true. (It's unclear to me what happens if neither
branch of the if/elif is true; there's no else case. Does it fall through?)  If
we're in GUI mode, calls `bluesky.ui.qtgl.start()` (which is actually defined in
`bluesky.ui.qtgl.gui`); else, if we're in "sim" mode, calls `bluesky.sim.start()`.

(Note that `bluesky.settings` parses the command line and a config file. It's
pretty convoluted.)

There appears to be a headless mode, perhaps used with the command-line argument
`--headless`.

### `bluesky.ui.qtgl.gui.start()`

Starts client/server model, I think. Some odd message-handling setup. Apparently
defaults (hard-coded!) are to use ports 9000 and 9001 for events and "streams"
respectively.

I _think_ eventually registers the client as `bluesky.net.start_discovery()`. Where
is the simulator in all this?

