#! /usr/bin/python2

# dual screen player
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
import ctypes
x11 = ctypes.cdll.LoadLibrary('libX11.so')
x11.XInitThreads()

import json
import gtk
import vlc
import math
import sched
import time
import pprint
import gc
import random
import time

from Queue import Queue 

from threading import Thread, Timer


from folderscan import VideoCollection

gtk.gdk.threads_init()

pp = pprint.PrettyPrinter(indent=4)

gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_UNCOLLECTABLE)
gc.disable()

q = Queue()


class VideoClass():

    def appInit(self):
        self.act = 3
        self.track = 2
        self.seq = 0

        self.instance = vlc.Instance("--no-audio", "--no-xlib", "--quiet", "--overlay")
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
        self.vlc_events = self.vright.player.event_manager()
        if 'videoCollection' not in globals():
            VideoCollection("/home/dolivari/Public/sequences/", self.scanDone)
        else:
            pp.pprint(videoCollection)

    def scanDone(self, collection):
        global videoCollection
        videoCollection = {
            "collection": collection
        }
        pp.pprint(videoCollection)
        

    def nextPlay(self):
        if len(videoCollection["collection"][self.act]["tracks"][self.track]["videos_left"]) <= self.seq:
            self.seq = 0
            self.act +=1
            if self.act < len(videoCollection["collection"]) :
                self.track = videoCollection["collection"][self.act]["tracks"][random.randint(0,len(videoCollection["collection"][self.act]["tracks"]))]
            else:
                self.act=0
                self.track=0
        self.play(self.act, self.track, self.seq)
        self.seq += 1
        
    def play(self, act,track,seq):
      
        if 0 <= act and 0 <= track and 0 <= seq:

            left_vid = videoCollection["collection"][act]["tracks"][track]["videos_left"][seq]["filename"]
            right_vid = videoCollection["collection"][act]["tracks"][track]["videos_right"][seq]["filename"]
            
            self.vleft.player.stop()
            self.vright.player.stop()
        
            self.vlc_events.event_detach(vlc.EventType.MediaPlayerPositionChanged)
            self.vlc_events.event_detach(vlc.EventType.MediaPlayerEndReached)
        
            gc.collect()

            self.media_left = self.instance.media_new(left_vid)
            self.vleft.player.set_media(self.media_left)

            self.media_right = self.instance.media_new(right_vid)
            self.vright.player.set_media(self.media_right)

            if(self.vleft.player.get_length() < self.vright.player.get_length()):
                self.vlc_events = self.vright.player.event_manager()
            else:
                self.vlc_events = self.vleft.player.event_manager()
            
            self.vlc_events.event_attach(
                vlc.EventType.MediaPlayerPositionChanged, self.positionChanged)

            self.vlc_events.event_attach(
                vlc.EventType.MediaPlayerEndReached, self.endReached)

            self.vright.player.event_manager().event_attach(
                vlc.EventType.MediaPlayerVout, self.openOnPlay)
            self.vleft.player.event_manager().event_attach(
                vlc.EventType.MediaPlayerVout, self.openOnPlay)


            print("Playing ",act,track,seq,left_vid)    
            self.vleft.player.play()
            self.vright.player.play()

        else:
            print("Bad play")

    def openOnPlay(self, evt):
        self.vleft.player.video_set_adjust_int(
            vlc.VideoAdjustOption.Enable, False)
        self.vright.player.video_set_adjust_int(
            vlc.VideoAdjustOption.Enable, False)

    def positionChanged(self, pos):
        percent = math.floor(self.vleft.player.get_position() * 10000) / 100
        print(percent)

    def endReached(self, foo):
        q.put("done")

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



class VLCWidget(gtk.DrawingArea):

    def __init__(self, instance):
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(0, 0, 0, 0))

        def handle_embed(*args):
            self.player.set_xwindow(self.window.xid)
            return True
        self.connect("map", handle_embed)
        self.set_size_request(1280, 720)


class VLCContainer(gtk.VBox):

    def __init__(self, instance):
        gtk.VBox.__init__(self)
        self._vlc_widget = VLCWidget(instance)
        self.player = self._vlc_widget.player
        self.pack_start(self._vlc_widget, expand=True)


local = VideoClass()
local.appInit()
local.nextPlay()
while True:
    q.get()
    print("done")
    local.nextPlay()
    
