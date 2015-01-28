#! /usr/bin/python2


from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
from threading import Thread

import json
import gtk
import vlc
import math

gtk.gdk.threads_init()
instance = vlc.Instance("--no-xlib")

class VideoClass(WebSocket):

    def appInit(self):
        window = gtk.Window()
        mainbox = gtk.VBox()
        videos = gtk.HBox()

        window.add(mainbox)
        mainbox.add(videos)
        self.vleft = VLCContainer()
        videos.add(self.vleft)
        self.vright = VLCContainer()
        videos.add(self.vright)

        window.show_all()
        window.connect("destroy", gtk.main_quit)
        Thread(target=gtk.main).start()

    def play(self, prefix):

        print("play",prefix)

        self.vleft.player.set_media(
            instance.media_new(prefix + 'G_.mp4'))
        self.vright.player.set_media(
            instance.media_new(prefix + 'D_.mp4'))

        if(self.vleft.player.get_length() < self.vright.player.get_length()):
            self.vlc_events = self.vright.player.event_manager()
        else:
            self.vlc_events = self.vleft.player.event_manager()

        self.vlc_events.event_attach(
            vlc.EventType.MediaPlayerPositionChanged, self.positionChanged)

        self.vleft.player.play()
        self.vright.player.play()


    def positionChanged(self,pos):
        msg = {
            "left_screen": {
                "time": self.vleft.player.get_time() // 1000,
                "length": self.vleft.player.get_length() // 1000,
                "pos": math.floor(self.vleft.player.get_position() * 10000) / 100,
                "mrl": self.vleft.player.get_media().get_mrl()
            },
            "right_screen": {
                "time": self.vright.player.get_time() // 1000,
                "length": self.vright.player.get_length() // 1000,
                "pos": math.floor(self.vright.player.get_position() * 10000) / 100,
                "mrl": self.vright.player.get_media().get_mrl()
            }
        }
        self.sendMessage(json.dumps(msg))

    def handleConnected(self):
        print(self.address, "connected")

    def handleClose(self):
        print self.address, 'closed'
        gtk.main_quit()

    def handleMessage(self):
        if self.data is None:
            self.data = ""
        msg = json.loads(self.data.decode())

    def handleMessage(self):
        if self.data is None:
            self.data = ""
        msg = json.loads(self.data.decode())
        if("command" in msg):
            try:
                if(msg["command"] == "init"):
                    self.appInit()
                if(msg["command"] == "play"):
                    prefix = msg["prefix"]
                    self.play(prefix)
            except Exception as e:
                print("Exception", e)


class VLCWidget(gtk.DrawingArea):

    def __init__(self, *p):
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()

        def handle_embed(*args):
            self.player.set_xwindow(self.window.xid)
            return True
        self.connect("map", handle_embed)
        self.set_size_request(320, 180)


class VLCContainer(gtk.VBox):

    def __init__(self, *p):
        gtk.VBox.__init__(self)
        self._vlc_widget = VLCWidget(*p)
        self.player = self._vlc_widget.player
        self.pack_start(self._vlc_widget, expand=True)


if __name__ == '__main__':
    server = SimpleWebSocketServer("", 8888, VideoClass)
    server.serveforever()
