#! /usr/bin/python2

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


from pymediainfo import MediaInfo

import os
import re
import pprint
import json


class VideoCollection:

    def __init__(self, path, callback):
        self.collection = [None, None, None, None, None, None, None, None]
        for f in sorted(os.listdir(path)):
            filename = path + f
            print(filename)
            media_info = MediaInfo.parse(filename)
            m = re.match(r"A(\d)_P(\d)_V(\d{2})_(.)_(.*)\.mp4", f)
            act = int(m.group(1))
            track = int(m.group(2))
            sequence = int(m.group(3))
            side = m.group(4)
            info = m.group(5)
            duration = media_info.tracks[0].duration
            #print(act, track, sequence, side, info, duration)
            if(self.collection[act] is None):
                self.collection[act] = {
                    "act": act,
                    "tracks": [None, None, None, None, None]
                }
            if(self.collection[act]["tracks"][track] is None):
                self.collection[act]["tracks"][track] = {
                    "track": track,
                    "videos_left": [],
                    "videos_right": [],
                    "duration_left": 0,
                    "duration_right": 0,
                }

            if(side == "G"):
                self.collection[act]["tracks"][track]["videos_left"].append({
                    "filename": filename,
                    "name": f,
                    "duration": duration,
                    "sequence": sequence
                })
                self.collection[act]["tracks"][track][
                    "duration_left"] += duration
            if(side == "D"):
                self.collection[act]["tracks"][track]["videos_right"].append({
                    "filename": filename,
                    "name": f,
                    "duration": duration,
                    "sequence": sequence
                })
                self.collection[act]["tracks"][track][
                    "duration_right"] += duration

        self.collection = filter(None, self.collection)
        for act in self.collection:
            act["tracks"] = filter(None, act["tracks"])
        #pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.collection)
        callback(self.collection)


if __name__ == '__main__':
    VideoCollection(".")
