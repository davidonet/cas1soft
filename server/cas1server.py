#! /usr/bin/python2


from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer

from threading import Thread

import json
import gtk
import vlc
import math
from folderscan import VideoCollection


gtk.gdk.threads_init()
instance = vlc.Instance("--no-xlib")
Thread(target=gtk.main).start()


class VideoClass(WebSocket):

    def appInit(self):
        self.window = gtk.Window()
        mainbox = gtk.VBox()
        videos = gtk.HBox()
        self.window.add(mainbox)
        mainbox.add(videos)
        self.vleft = VLCContainer()
        videos.add(self.vleft)
        self.vright = VLCContainer()
        videos.add(self.vright)
        self.window.show_all()
        if 'videoCollection' not in globals():
            Thread(target=VideoCollection, args=(
                "/home/dolivari/Public/sequences/", self.scanDone)).start()
        else:
            self.sendMessage(json.dumps(videoCollection))

    def scanDone(self, collection):
        global videoCollection
        videoCollection = {
            "collection": collection
        }
        self.sendMessage(json.dumps(videoCollection))

    def play(self, msg):

        left_vid = videoCollection["collection"][msg["actidx"]]["tracks"][
            msg["trackidx"]]["videos_left"][msg["sequenceidx"]]["filename"]

        right_vid = videoCollection["collection"][msg["actidx"]]["tracks"][
            msg["trackidx"]]["videos_right"][msg["sequenceidx"]]["filename"]

        self.vleft.player.set_media(
            instance.media_new(left_vid))
        self.vright.player.set_media(
            instance.media_new(right_vid))

        if(self.vleft.player.get_length() < self.vright.player.get_length()):
            self.vlc_events = self.vright.player.event_manager()
        else:
            self.vlc_events = self.vleft.player.event_manager()

        self.vlc_events.event_attach(
            vlc.EventType.MediaPlayerPositionChanged, self.positionChanged)

        self.vleft.player.play()
        self.vright.player.play()

    def positionChanged(self, pos):
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
        self.vleft.player.stop()
        self.vright.player.stop()
        self.window.destroy()

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
                    self.play(msg)
                if(msg["command"] == "collection"):
                    print(self.collection)
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
    try:
        server.serveforever()
    except KeyboardInterrupt:
        gtk.main_quit()
        server.close()
