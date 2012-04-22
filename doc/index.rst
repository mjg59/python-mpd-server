.. python-mpd-server documentation master file, created by
   sphinx-quickstart on Wed Mar 28 00:03:28 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2

Welcome to python-mpd-server's documentation!
============================================= 

python-mpd-server permits to bind a player to a MPD server. 

You then can control your player with a MPD client such as sonata or
gmpc. This module defines a server which manages client requests,
parses a request and generates a respond. A MPD command is a class
that you can override.

Current supported features are:

- Manage a playlist (add, move, delete, ...)
- Store/Load playlist
- Playback control (play, stop, next, ...)


Getting Started
---------------
An example of a basic use is available in :ref:`example`.

Python-mpd-server library defines a default server in :mod:`mpdserver` module
and some defaults commands in :mod:`command` module.

To launch the server, you just have to create a Mpd object ::

   mpd=mpdserver.Mpd(listening_port)

This simulates a dummy mpd server which works with sonata, mpc and gmpc. 
To bind an existing player with mpd commmand, you then have to redefine commands.
For example, to bind play command with your player ::

    class Play(mpdserver.Command):
        def handle_args(self):yourplayer.play()
    mpdserver.MpdRequestHandler.commands['play']=Play

Launching python mpd server
----------------------------------
.. automodule:: mpdserver
   :members:


Defining Commands
----------------------------------
.. automodule:: command_base
   :members:

Command Squeletons
-------------------
.. automodule:: command_skel
   :members:



.. _example:

Basic Example
-------------
This is a simple example of how to use python-mpd-server.

.. literalinclude:: mpd_server_example.py


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

