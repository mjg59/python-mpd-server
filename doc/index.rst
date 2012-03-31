.. python-mpd-server documentation master file, created by
   sphinx-quickstart on Wed Mar 28 00:03:28 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-mpd-server's documentation!
============================================= 

Getting Started
---------------

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

Bind a player to python-mpd-server
----------------------------------

:class:`mpdserver.Command` is a command base class, all commands inherit from
it. A :class:`Command` contains command arguments definition. You can
handle them with :meth:`Command.handle_args`.


.. toctree::
   :maxdepth: 2

.. automodule:: mpdserver
   :members:
.. autoclass:: Command
   :members:


.. automodule:: command
   :members:





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

