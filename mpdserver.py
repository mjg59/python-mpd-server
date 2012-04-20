""" This module permits to use mpd client to control another player.

To launch a mpd server, use :class:`Mpd`. :class:`MpdRequestHandler`
treats a client connection. Supported command are listed in
:attr:`MpdRequestHandler.commands`. For more informations about
command definition, see :class:`command.Command`


"""
import SocketServer
SocketServer.TCPServer.allow_reuse_address = True
import time
import re 
import threading
import sys
#from pimp.core.playlist import * 
#from pimp.core.player import * 
#import pimp.core.db
import logging

from command_base import *
from command_skel import *

logger=logging
#logger.basicConfig(level=logging.INFO)
logger.basicConfig(level=logging.DEBUG)

#logger.setLevel(logging.DEBUG)

class MpdServer(SocketServer.ThreadingMixIn,SocketServer.TCPServer):
    """Treat a request from mpd clients. It takes a
    :class:`RequestHandlerClass` which define supported commands."""
    def __init__(self,RequestHandlerClass,port=6600):
        HOST, PORT = "", port
        SocketServer.TCPServer.__init__(self,(HOST, PORT),RequestHandlerClass)



##################################
### Mpd supported return types ###
##################################
class MpdErrorMsgFormat(Exception):pass
class MpdCommandError(Exception):
    def __init__(self,msg="Unknown error",command="command is not specified"):
        self.command=command
        self.msg=msg
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} %s\n" % (self.command,self.msg)
class CommandNotSupported(MpdCommandError):
    def __init__(self,commandName):
        self.commandName=commandName
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} Command '%s' not supported\n" % (self.commandName,self.commandName)
class CommandNotImplemented(MpdCommandError):
    def __init__(self,commandName,message=""):
        self.commandName=commandName
        self.message=message
    def toMpdMsg(self):
        return "ACK [error@command_listNum] {%s} Command '%s' is not implemented (%s)\n" % (self.commandName,self.commandName,self.message)

class User(object):
    user=None
    def set_user(self,username):
        self.user=username
    def get_user(self):
        return self.user
        

class MpdRequestHandler(SocketServer.StreamRequestHandler):
    """ Manage the connection from a mpd client. Each client
    connection instances this object."""
    Playlist=MpdPlaylist
    commands={'currentsong':CurrentSong,
              'outputs':Outputs,
              'status':Status,
              'stats':Stats,
              'notcommands':NotCommands,
              'commands':Commands,
              'lsinfo':LsInfo,
              'tagtypes':TagTypes,
              'playlistinfo':PlaylistInfo,
              'playlistid':PlaylistId,
              'listplaylistinfo':ListPlaylistInfo,
              'plchanges':PlChanges,
              'moveid':MoveId,
              'move':Move,
              'delete':Delete,
              'deleteid':DeleteId,
              'add':Add,
              'plchangesposid':PlChangesPosId,
              'password':Password
             }
    """ Dict of supported commands. The key is the mpd command, the
    value the class which treats this command. """

    def __init__(self, request, client_address, server):
        self.playlist=self.Playlist()
        self.user=User()
        logger.debug( "Client connected (%s)" % threading.currentThread().getName())
        SocketServer.StreamRequestHandler.__init__(self,request,client_address,server)

    def handle(self):
        """ Handle connection with mpd client. It gets client command,
        execute it and send a respond."""
        welcome=u"OK MPD 0.13.0\n"
        self.request.send(welcome.encode("utf-8"))
        while True:
            msg=""
            try:
                cmdlist=None
                cmds=[]
                while True:
                    self.data = self.rfile.readline().strip()
                    if len(self.data)==0 : raise IOError #To detect last EOF
                    if self.data == "command_list_ok_begin":
                        cmdlist="list_ok"
                    elif self.data == "command_list_begin":
                        cmdlist="list"
                    elif self.data == "command_list_end":
                        break
                    else:
                        cmds.append(self.data)
                        if not cmdlist:break
                logger.debug("Commands received from %s" % self.client_address[0])
                try:
                    for c in cmds:
                        logger.debug("Command '" + c + "'...")
                        msg=msg+self.cmdExec(c)
                        if cmdlist=="list_ok" :  msg=msg+"list_OK\n"
                except MpdCommandError as e:
                    msg=e.toMpdMsg()
                except : raise
                else:
                    msg=msg+"OK\n"
                logger.debug("Message sent:\n\t\t"+msg.replace("\n","\n\t\t"))
                umsg=unicode(msg,"utf-8",errors='replace')
                self.request.send(umsg.encode("utf-8"))
            except IOError,e:
                logger.debug("Client disconnected (%s)"% threading.currentThread().getName())
                break

    def cmdExec(self,c):
        """ Execute mpd client command. Take a string, parse it and
        execute the corresponding server.Command function."""
        try:
            pcmd=[m.group() for m in re.compile('(\w+)|("([^"])+")').finditer(c)] # WARNING An argument cannot contains a '"'
            cmd=pcmd[0]
            args=[a[1:len(a)-1] for a in pcmd[1:]]
            logger.debug("Command executed : %s %s by user '%s'" % (cmd,args,self.user.get_user()))
            if not self.commands.has_key(cmd):
                logger.warning("Command '%s' is not supported!" % cmd)
                raise CommandNotSupported(cmd)
            msg=self.commands[cmd](args,playlist=self.playlist,user=self.user).run()
        except MpdCommandError : raise
        except CommandNotSupported : raise
        except :
            logger.critical("Unexpected error on command %s: %s" % (c,sys.exc_info()[0]))
            raise
        logger.debug("Respond:\n\t\t"+msg.replace("\n","\n\t\t"))
        return msg


class Mpd(object):
    """ Create the mpd handle server, binding to localhost on port 'port'.
    If port is not specified, the default MpdHandler port is used (6600).
    Mpd server is deamonized, but you can use wait method."""
    def __init__(self,port=None,mpdRequestHandler=MpdRequestHandler):
        logger.info("Mpd Server is listening on port " + str(port))
        if port:
            Mpd.server=MpdServer(mpdRequestHandler,port)
        else:
            Mpd.server=MpdServer(mpdRequestHandler)
            
        Mpd.thread = threading.Thread(target=Mpd.server.serve_forever)
        Mpd.thread.setDaemon(True)
        Mpd.thread.start()
        logger.debug(("mpd",Mpd.thread))
        
    def quit(self):
        """ Stop mpd server """
        Mpd.server.shutdown()

    def wait(self,timeout=None):
        """ Return True if mpd is alive, False otherwise."""
        if timeout==None:
            Mpd.thread.join()
        else:
            Mpd.thread.join(timeout)
        return Mpd.thread.isAlive()
        
