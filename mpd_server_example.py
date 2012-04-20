#!/usr/bin/python
""" This is a simple howto example."""
import mpdserver


class Outputs(mpdserver.Outputs):
    def items(self):
        return [('outputid',0),        # <int output> the output number                              
                ('outputname','test here'), # <str name> the name as defined in the MPD configuration file
                ('outputenabled',1)    # <int enabled> 1 if enabled, 0 if disabled                   
                ]


class MpdPlaylist(mpdserver.MpdPlaylist):
    playlist=[mpdserver.MpdPlaylistSong(file='file0',songId=0,playlistPosition=0,title='title0',time=0,album='album0',artist='artist0',track=0)]
    def songIdToPosition(self,i):
        for e in self.playlist:
            if e.id==i : return e.playlistPosition
            
    def handlePlaylist(self):
        print 'iuoo'
        return self.playlist

    def move(self,i,j):
        print "move "
        self.playlist[i],self.playlist[j]=self.playlist[j],self.playlist[i]

class PlayId(mpdserver.PlayId):
    def handle_args(self,songId):print "iop"


mpdserver.MpdRequestHandler.commands['outputs']=Outputs
mpdserver.MpdRequestHandler.commands['playid']=PlayId
mpdserver.MpdRequestHandler.Playlist=MpdPlaylist

print "Starting a mpd server on port 9999"
print "Type Ctrl+C to exit\n"
mpd=mpdserver.Mpd(9999)

if __name__ == "__main__":
    try:
        while mpd.wait(1) : pass
    except KeyboardInterrupt:
        print "Stopping mpd server"
        mpd.quit()


