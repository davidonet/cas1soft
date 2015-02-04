#! /usr/bin/python2

# dual screen player with websocket interface
# Copyright (C) 2014 David Olivari
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
# based on gtk example/widget for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#


import json
import gtk
import vlc
import math
import sched
import time
import pprint
import gc

from threading import Thread, Timer

from folderscan import VideoCollection
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer

gtk.gdk.threads_init()

pp = pprint.PrettyPrinter(indent=4)

gc.set_debug(gc.DEBUG_STATS  | gc.DEBUG_UNCOLLECTABLE)
gc.disable()

class VideoClass(WebSocket):

    def appInit(self):
        self.instance = vlc.Instance("--no-xlib", "--no-audio","--quiet")
        self.window = gtk.Window()
        mainbox = gtk.VBox()
        videos = gtk.HBox()
        self.window.add(mainbox)
        mainbox.add(videos)
        self.vleft = VLCContainer(self.instance)
        videos.add(self.vleft)
        self.vright = VLCContainer(self.instance)
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

        if 0 <= msg["actidx"] and 0 <= msg["trackidx"] and 0 <= msg["sequenceidx"]:

            left_vid = videoCollection["collection"][msg["actidx"]]["tracks"][
                msg["trackidx"]]["videos_left"][msg["sequenceidx"]]["filename"]

            right_vid = videoCollection["collection"][msg["actidx"]]["tracks"][
                msg["trackidx"]]["videos_right"][msg["sequenceidx"]]["filename"]

            self.currentSeq = msg

            self.vleft.player.stop()
            self.vright.player.stop()
            gc.collect()

            self.vleft.player.set_media(
                self.instance.media_new(left_vid))

            self.vright.player.set_media(
                self.instance.media_new(right_vid))

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

        else:
            print("Bad play")

    def pause(self):
        self.vleft.player.pause()
        self.vright.player.pause()

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
        msg = self.currentSeq
        msg["left_screen"] = {
            "time": self.vleft.player.get_time() // 1000,
            "length": self.vleft.player.get_length() // 1000,
            "pos": math.floor(self.vleft.player.get_position() * 10000) / 100,
            "mrl": self.vleft.player.get_media().get_mrl()
        }
        msg["right_screen"] = {
            "time": self.vright.player.get_time() // 1000,
            "length": self.vright.player.get_length() // 1000,
            "pos": math.floor(self.vright.player.get_position() * 10000) / 100,
            "mrl": self.vright.player.get_media().get_mrl()
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
        pp.pprint(msg)
        if("command" in msg):
            try:
                if(msg["command"] == "init"):
                    self.appInit()
                if(msg["command"] == "play"):
                    self.play(msg)
                if(msg["command"] == "fadeout"):
                    self.fadeOut()
                if(msg["command"] == "pause"):
                    self.pause()
            except Exception as e:
                print("Exception", e)
                pp.pprint(msg)


class VLCWidget(gtk.DrawingArea):

    def __init__(self,instance):
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))

        def handle_embed(*args):
            self.player.set_xwindow(self.window.xid)
            return True
        self.connect("map", handle_embed)
        self.set_size_request(320, 180)


class VLCContainer(gtk.VBox):

    def __init__(self, instance):
        gtk.VBox.__init__(self)
        self._vlc_widget = VLCWidget(instance)
        self.player = self._vlc_widget.player
        self.pack_start(self._vlc_widget, expand=True)


if __name__ == '__main__':
    server = SimpleWebSocketServer("", 8888, VideoClass)
    try:
        server.serveforever()
    except KeyboardInterrupt:
        gtk.main_quit()
        server.close()
    except Exception as e:
        print("Exception", e)
