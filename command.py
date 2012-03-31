import logging
import mpdserver
logger=mpdserver.logging
#logger.basicConfig(level=logging.DEBUG)


class CommandArgumentException(Exception):pass
        

class Command():
    """ You can define argument format by setting formatArg
    attribute. Command argument can be accessed with self.args
    dictionnary. 

    Each command has a playlist attribute which is given by
    MpdRequestHandler. This playlist must implement MpdPlaylist class
    and by default, this one is used.
    """
    formatArg=[]
    def __init__(self,args,playlist):
            self.args=self.__parseArg(args)
            self.playlist=playlist

    def run(self):
        try:
            self.handle_args(**(self.args))
            return self.toMpdMsg()
        except NotImplementedError as e:
            raise mpdserver.CommandNotImplemented(self.__class__,str(e))

    def __parseArg(self,args):
        if len(args) > len(self.formatArg):
            raise CommandArgumentException("Too much arguments: %s command arguments should be %s instead of %s" % (self.__class__,self.formatArg,args))
        try:
            d=dict()
            for i in range(0,len(self.formatArg)):
                if Opt in self.formatArg[i][1].__bases__ :
                    try:
                        d.update({self.formatArg[i][0] : self.formatArg[i][1](args[i])})
                    except IndexError : pass
                else:                        
                    d.update({self.formatArg[i][0] : self.formatArg[i][1](args[i])})
        except IndexError : 
            raise CommandArgumentException("Not enough arguments: %s command arguments should be %s instead of %s" %(self.__class__,self.formatArg,args))
        except ValueError as e:
            raise CommandArgumentException("Wrong argument type: %s command arguments should be %s instead of %s (%s)" %(self.__class__,self.formatArg,args,e))
        return d
        
    def handle_args(self,**kwargs):logger.debug("Parsing arguments %s in %s" % (str(kwargs),str(self.__class__)))
    def toMpdMsg(self):
        logger.debug("Not implemented respond for command %s"%self.__class__)
        return ""

class CommandDummy(Command):
    def toMpdMsg(self):
        logger.info("Dummy respond sent for command %s"%self.__class__)
        return "ACK [error@command_listNum] {%s} Dummy respond for command '%s'\n" % (self.__class__,self.__class__)
    

class CommandItems(Command):
    def items(self):return []
    def toMpdMsg(self):
        items=self.items()
        acc=""
        for (i,v) in items:
            acc+="%s: %s\n"%(i,str(v))
        return acc


class CommandSong(CommandItems):
    """ Generate songs information for mpd clients """
    def helper_mkSong(self,file,title=None,time=0,album=None,artist=None,track=0,playlistPosition=0,id=0):
        """ Helpers to create a mpd song """
        ret=[('file',file),
             ('Time',time)]
        if not album:
            ret+=[('Album',album)]
        if not artist:
            ret+=[('Artist',artist)]
        if not title:
            ret+=[('Title',title)]
        ret+=[('Track',track),
              ('Pos',playlistPosition),
              ('Id',id)]
        return ret
    def song(self):return [] #self.helper_mkSong("/undefined/")
    """ Override it to adapt this command """
    def items(self):return self.song()
        

import types
class Opt(object):pass
class OptInt(Opt,types.IntType):pass
class OptStr(Opt,types.StringType):pass

class MpdSong(object):
    """ To create a mpd song. To kind of mpd song exist : in a playlist or not.
    If songId is not set, an id is generated with generatePlaylistSongId method."""

    def __init__(self,file,title="",time=0,album="",artist="",track=0,playlistPosition=None,songId=None):
        self.file=file
        self.title=title
        self.time=time
        self.album=album
        self.artist=artist
        self.track=track
        self.playlistPosition=playlistPosition
        if songId == None:
            self.id=self.generatePlaylistSongId(self)
        else:
            self.id
    def generatePlaylistSongId(self,song):
        return id(song)

class PlaylistHistory(object):
    """ Contains all playlist version to generate playlist diff (see
    plchanges* commands). This class is a singleton and it is used by
    MpdPlaylist.    
    """ 
    _instance = None
    playlistHistory=[]
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PlaylistHistory, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance
        
    def addPlaylist(self,version,playlist):
        """ Add playlist version if not exist in history """
        for (v,p) in self.playlistHistory:
            if v == version:
                return None
        self.playlistHistory.append((version,playlist))

    def getPlaylist(self,version):
        """ Get playlist from version"""
        for (i,p) in self.playlistHistory:
            if i==version:
                return p
        return None

    def diff(self,version):
        """ Return new songs in current playlist since version """
        plOld=self.getPlaylist(version)
        plCur=self.playlistHistory[len(self.playlistHistory)-1][1]
        if plOld == None:
            return plCur
        diff=[]
        try :
            for i in range(0,len(plOld)):
                if plOld[i] != plCur[i]:
                    diff.append(plCur[i])
            for i in range(len(plOld),len(plCur)):
                diff.append(plCur[i])
        except IndexError: pass
        return diff
            
    def show(self):
        print "show playlistHistory"
        print "number of version: " + str(len(self.playlistHistory))
        for i in self.playlistHistory:
            print i
            print "------"
        print "show playlistHistory end"
        

class MpdPlaylist(object):
    """ MpdPlaylist is a list of song.  
    Use it to create a mapping between your player and the fictive mpd
    server.

    Some methods must be implemented, otherwise, NotImplementedError
    is raised.

    To bind a playlist to this class, use overide
    :method:`handlePlaylist` method.
    """
    def __init__(self):
        self.playlistHistory=PlaylistHistory()

    def handlePlaylist(self):
        raise NotImplementedError("you should implement MpdPlaylist.handlePlaylist method")

    def generateMpdPlaylist(self):
        p=self.handlePlaylist()
        for i in range(len(p)):
            p[i]['playlistPosition']=i
        self.playlistHistory.addPlaylist(self.version(),p)
        return p

    def generateMpdPlaylistDiff(self,oldVersion):
        self.generateMpdPlaylist()
        return self.playlistHistory.diff(oldVersion)

    def songIdToPosition(self,id):
        raise NotImplementedError("you should implement MpdPlaylist.songIdToPosition method")
    def version(self):
        return 0
    def length(self):
        return len(self.generateMpdPlaylist())
    def move(self,fromPostion,toPosition):
        raise NotImplementedError("you should implement MpdPlaylist.move method")
    def moveId(self,fromId,toPosition):
        self.move(self.songIdToPosition(fromId),toPosition)
    def delete(self,position):
        raise NotImplementedError("you should implement MpdPlaylist.delete method")
    def deleteId(self,songId):
        self.delete(self.songIdToPosition(songId))
        


class CommandPlaylist(CommandSong):
    def handle_playlist(self):
        """ Overwrite it to specify a real playlist. 
        Should return a list of dict song informations"""
        return self.playlist.generateMpdPlaylist()

    def items(self):
        playlist=self.handle_playlist()
        acc=[]
        for s in playlist:
            acc+=self.helper_mkSong(**s)
        return acc

################################
# Default Commands Definitions #
################################
class PlayId(Command):
    formatArg=[('songId',OptInt)]

class Pause(Command):
    """ Override handle_pause and handle_unpause method """
    formatArg=[('state',int)]
    def handle_args(self,state): 
        if state==1:
            self.handle_pause()
        else :
            self.handle_unpause()
    def handle_pause(self):pass
    def handle_unpause(self):pass

class Seek(Command):
    """Skip to a specified point toSec in a song songPosition on the playlist"""
    formatArg=[('songPosition',int),('toSec',int)]


class PlayId(Command):
    formatArg=[('songId',OptInt)]

    
class Outputs(CommandItems):
    def items(self):
        return [('outputid',0),        # <int output> the output number                              
                ('outputname','test'), # <str name> the name as defined in the MPD configuration file
                ('outputenabled',1)    # <int enabled> 1 if enabled, 0 if disabled                   
                ]

class CurrentSong(CommandSong):pass

class Stats(CommandItems):
    def items(self):
        return [("artists",-1),  #number of artists
                ("albums",-1),  #number of albums
                ("songs",-1),  #number of songs
                ("uptime",-1),  #daemon uptime (time since last startup) in seconds
                ("playtime",-1),  #time length of music played
                ("db_playtime",-1),  #sum of all song times in db
                ("db_update",-1)]  #last db update in UNIX time 

class Status(CommandItems):
    def helper_status_common(self,volume=0,repeat=0,random=0,xfade=0):
        "Status is set to 'stop' by default. Use :method:play or :method:pause to set status"
        return [('volume',volume), #(0-100)  
                ('repeat',repeat), #(0 or 1) 
                ('random',random), #(0 or 1) 
                ('playlist',self.playlist.version()), #(31-bit unsigned integer, the playlist version number)
                ('playlistlength',self.playlist.length()),   #(integer, the length of the playlist)                 
                ('xfade',xfade)]                     #(crossfade in seconds)                                
#               ('bitrate') + #<int bitrate> (instantaneous bitrate in kbps)
#               ('audio') + #<int sampleRate>:<int bits>:<int channels>
#               ('updating_db') + #<int job id>
#               ('error') + #if there is an error, returns message here
#               ('nextsong: 0\n') + #(next song, playlist song number >=mpd 0.15)
#               ('nextsongid: 0\n') + #(next song, playlist songid>=mpd 0.15)

    def helper_status_stop(self,volume=0,repeat=0,random=0,xfade=0):
        "Status is set to 'stop' by default. Use :method:play or :method:pause to set status"
        return (self.helper_status_common(volume,repeat,random,xfade) +
                [('state',"stop")]) #("play", "stop", or "pause")
    
    def helper_status_play(self,volume=0,repeat=0,random=0,xfade=0,elapsedTime=10,durationTime=100,playlistSongNumber=-1,playlistSongId=-1):
        return (self.helper_status_common(volume,repeat,random,xfade) +
                [('state',"play"),
                 ('song',playlistSongNumber), #(current song stopped on or playing, playlist song number)
                 ('songid',playlistSongId),   #(current song stopped on or playing, playlist songid)
                 ('time',"%d:%d"%(elapsedTime,durationTime))]) #<int elapsed>:<time total> (of current playing/paused song)

    def helper_status_pause(self,volume=0,repeat=0,random=0,xfade=0,elapsedTime=10,durationTime=100,playlistSongNumber=-1,playlistSongId=-1):
        return (self.helper_status_common(volume,repeat,random,xfade) +
                [('state',"pause"),
                 ('song',playlistSongNumber),
                 ('songid',playlistSongId),
                 ('time',"%d:%d"%(elapsedTime,durationTime))])

    def items(self):
        return self.helper_status_stop()

class NotCommands(CommandItems): pass# Not used by gmpc
    # def items(self):
    #     return [('command','tagtypes'),
    #             ('command','lsinfo')]

class LsInfo(CommandItems): # Since 0.12
    formatArg=[('directory',OptStr)]

class MoveId(Command): # Since 0.12
    formatArg=[('idFrom',int),('positionTo',int)]
    def handle_args(self,idFrom,positionTo):
        self.playlist.moveId(idFrom,positionTo)
class Move(Command): # Since 0.12
    formatArg=[('positionFrom',int),('positionTo',int)]
    def handle_args(self,positionFrom,positionTo):
        self.playlist.move(positionFrom,positionTo)

class Delete(Command): # Since 0.12
    formatArg=[('songPosition',int)]
    def handle_args(self,songPosition):
        self.playlist.delete(songPosition)
class DeleteId(Command): # Since 0.12
    formatArg=[('songId',int)]
    def handle_args(self,songId):
        self.playlist.deleteId(songId)

        
    
class ListPlaylistInfo(CommandSong): # Since 0.12
    """ List playlist 'playlistname' content """
    formatArg=[('playlistName',str)]

class Add(Command): # todo return type
    formatArg=[('song',str)]

class TagTypes(Command):pass # Since 0.12

class PlaylistInfo(CommandPlaylist):
    """ Without song position, list all song in current playlist. With
    song position argument, get song details. """
    formatArg=[('songPosition',OptInt)]
    def handle_playlist(self):
        try :
            return [self.playlist.generateMpdPlaylist()[self.args['songPosition']]]
        except KeyError:pass
        return self.playlist.generateMpdPlaylist()

class PlaylistId(CommandPlaylist):
    """ Without song position, list all song in current playlist. With
    song position argument, get song details. """
    formatArg=[('songId',OptInt)]
    def handle_args(self,songId):
        print songId
    def handle_playlist(self):
        try :
            print "songId in playlistId" + str(self.args['songId'])
            idx=self.playlist.songIdToPosition(self.args['songId'])
            print "idx " + str(idx)
            return [self.playlist.generateMpdPlaylist()[idx]]
        except KeyError:pass
        return self.playlist.generateMpdPlaylist()


class SetVol(Command):
    formatArg=[('volume',int)]
    
class PlChanges(CommandPlaylist):
    formatArg=[('playlistVersion',int)]
    def handle_playlist(self):
        return self.playlist.generateMpdPlaylistDiff(self.args['playlistVersion'])
    
class PlChangesPosId(CommandItems):
    formatArg=[('playlistVersion',int)]
    def items(self):
        p=self.playlist.generateMpdPlaylistDiff(self.args['playlistVersion'])
        acc=[]
        for s in p:
            acc.append(('cpos',s['playlistPosition']))
            acc.append(('Id',s['id']))
        return acc


class Password(Command):
    formatArg=[('pwd',str)]





class MpdReturnType(object):
    def checkType(self,cls,cls2=None):
        if type(self) is cls or (cls2!=None and type(self) is cls2):
            return self.toMpdMsg()
        else: raise MpdErrorMsgFormat
    def toMpdMsg(self):
        logger.info("Dummy respond sent for command %s"%type(self))
        return ""


# class MpdPlaylist(MpdReturnType):
#     def __init__(self):
#         print "initialisation playlist"
#         self.playlist=[]
#         self.version=0
        
#     def update(self):
#         """ Override it to map your playlist to a mpd playlist. """
#         self.playlist=[MpdSong("undefined 0"),MpdSong("undefined 1")]

#     def toMpdMsg(self):
#         self.update()
#         acc=""
#         for i in self.playlist:
#             acc+=i.toMpdMsg()
#         return acc



# class Commands(MpdReturnType): # Not used by gmpc
#     def toMpdMsg(self):
#         return (("command: status\n")  #number of artists
#                 + ("command: outputs\n")
#                 + ("command: pause\n") 
#                 + ("command: stop\n")
#                 + ("command: play\n")
#                 )
