#! /usr/bin/python

#
# gtk example/widget for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
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

"""VLC Gtk Widget classes + example application.

This module provides two helper classes, to ease the embedding of a
VLC component inside a pygtk application.

VLCWidget is a simple VLC widget.

DecoratedVLCWidget provides simple player controls.

When called as an application, it behaves as a video player.

$Id$
"""

import gtk
import gobject
gtk.gdk.threads_init()

from threading import Thread

import sys
import vlc
import json

from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer


class SimpleEcho(WebSocket):

    def handleMessage(self):
        if self.data is None:
            self.data = ''
        print(self.data)
        # echo message back to client
        self.sendMessage(str(self.data))

    def handleConnected(self):
        window = gtk.Window()
        mainbox = gtk.VBox()
        videos = gtk.HBox()

        window.add(mainbox)
        mainbox.add(videos)

        # Create VLC widgets
        self.v1 = DecoratedVLCWidget()
        self.v1.player.set_media(
            instance.media_new('/opt/storage/CAS1_SRC/ACTE 4/A4-P1/CAS1_A4P1V20G_.mp4'))
        videos.add(self.v1)
        self.v2 = DecoratedVLCWidget()
        self.v2.player.set_media(
            instance.media_new('/opt/storage/CAS1_SRC/ACTE 4/A4-P1/CAS1_A4P1V20D_.mp4'))
        videos.add(self.v2)

        if(self.v1.player.get_length()<self.v2.player.get_length()):
            self.vlc_events = self.v2.player.event_manager()
        else:
            self.vlc_events = self.v1.player.event_manager()

        self.vlc_events.event_attach(
            vlc.EventType.MediaPlayerPositionChanged, self.send_pos)
        window.show_all()
        window.connect("destroy", gtk.main_quit)

        self.v1.player.play()
        self.v2.player.play()

        Thread(target=gtk.main).start()
        print self.address, 'connected'

    def handleClose(self):
        print self.address, 'closed'
        gtk.main_quit()

    def send_pos(self, data):
        msg = {
            "left_screen": {
                "time": self.v1.player.get_time(),
                "length": self.v1.player.get_length(),
                "title": self.v1.player.get_media().get_mrl()
            },
            "right_screen": {
                "time": self.v2.player.get_time(),
                "length": self.v2.player.get_length(),
                "title": self.v2.player.get_media().get_mrl()
            }
        }
        self.sendMessage(json.dumps(msg))


server = SimpleWebSocketServer('', 8888, SimpleEcho)


from gettext import gettext as _

# Create a single vlc.Instance() to be shared by (possible) multiple players.
instance = vlc.Instance("--no-xlib")


class VLCWidget(gtk.DrawingArea):

    """Simple VLC widget.

    Its player can be controlled through the 'player' attribute, which
    is a vlc.MediaPlayer() instance.
    """

    def __init__(self, *p):
        gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()

        def handle_embed(*args):
            if sys.platform == 'win32':
                self.player.set_hwnd(self.window.handle)
            else:
                self.player.set_xwindow(self.window.xid)
            return True
        self.connect("map", handle_embed)
        self.set_size_request(320, 180)


class DecoratedVLCWidget(gtk.VBox):

    """Decorated VLC widget.

    VLC widget decorated with a player control toolbar.

    Its player can be controlled through the 'player' attribute, which
    is a Player instance.
    """

    def __init__(self, *p):
        gtk.VBox.__init__(self)
        self._vlc_widget = VLCWidget(*p)
        self.player = self._vlc_widget.player
        self.pack_start(self._vlc_widget, expand=True)
        #self._toolbar = self.get_player_control_toolbar()
        #self.pack_start(self._toolbar, expand=False)


class MultiVideoPlayer:

    """Example multi-video player.

    It plays multiple files side-by-side, with per-view and global controls.
    """

    def main(self, filenames):
        # Build main window
        server.serveforever()

if __name__ == '__main__':
    p = MultiVideoPlayer()
    p.main(sys.argv[1:])
