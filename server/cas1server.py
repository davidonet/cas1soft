#! /usr/bin/python2


import json
import gtk
import vlc
import math
import sched
import time

from threading import Thread, Timer

from folderscan import VideoCollection
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer

gtk.gdk.threads_init()
instance = vlc.Instance("--no-xlib")



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
        self.gtkthread = Thread(target=gtk.main).start()

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

        self.currentSeq = msg

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
        self.vlc_events.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.endReached)

        self.vleft.player.play()
        self.vleft.player.video_set_adjust_int(
            vlc.VideoAdjustOption.Enable, False)

        self.vright.player.play()
        self.vright.player.video_set_adjust_int(
            vlc.VideoAdjustOption.Enable, False)

        self.vleft.player.video_set_adjust_float(
            vlc.VideoAdjustOption.Brightness, 1.0)
        self.vright.player.video_set_adjust_float(
            vlc.VideoAdjustOption.Brightness, 1.0)
        self.vleft.player.video_set_adjust_float(
            vlc.VideoAdjustOption.Saturation, 1.0)
        self.vright.player.video_set_adjust_float(
            vlc.VideoAdjustOption.Saturation, 1.0)

    def fadeStep(self):
        self.vleft.player.video_set_adjust_int(
            vlc.VideoAdjustOption.Enable, True)
        self.vright.player.video_set_adjust_int(
            vlc.VideoAdjustOption.Enable, True)
        if(0 < self.brightness):
            self.vleft.player.video_set_adjust_float(
                vlc.VideoAdjustOption.Brightness, self.brightness / 100.0)
            self.vright.player.video_set_adjust_float(
                vlc.VideoAdjustOption.Brightness, self.brightness / 100.0)
            self.vleft.player.video_set_adjust_float(
                vlc.VideoAdjustOption.Saturation, self.brightness / 100.0)
            self.vright.player.video_set_adjust_float(
                vlc.VideoAdjustOption.Saturation, self.brightness / 100.0)
            self.brightness -= .5
            self.fadetimer = Timer(.05, self.fadeStep, ())
            self.fadetimer.start()
        else:
            self.vleft.player.video_set_adjust_float(
                vlc.VideoAdjustOption.Brightness, 0.0)
            self.vright.player.video_set_adjust_float(
                vlc.VideoAdjustOption.Brightness, 0.0)
            self.vleft.player.stop()
            self.vright.player.stop()
            self.sendMessage(json.dumps({"fadefinished": True}))

    def fadeOut(self):
        self.vleft.player.video_set_adjust_int(
            vlc.VideoAdjustOption.Enable, True)
        self.vright.player.video_set_adjust_int(
            vlc.VideoAdjustOption.Enable, True)
        self.brightness = 100.0
        self.fadeStep()

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

    def endReached(self, foo):
        msg = self.currentSeq
        msg["endreached"] = True
        self.sendMessage(json.dumps(msg))

    def handleConnected(self):
        print(self.address, "connected")

    def handleClose(self):
        print self.address, 'closed'

        try:
            self.vleft.player.stop()
        except:
            pass
        try:
            self.vright.player.stop()
        except:
            pass
        try:
            self.window.destroy()
        except:
            pass
        try:
            self.fadetimer.cancel()
        except:
            pass
        try:
            gtk.main_quit()
        except:
            pass  
        
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
                if(msg["command"] == "fadeout"):
                    self.fadeOut()
            except Exception as e:
                print("Exception", e)


class VLCWidget(gtk.DrawingArea):

    def __init__(self, *p):
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))

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