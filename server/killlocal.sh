#!/bin/sh

kill -9 `ps aux | grep "python2 cas1local.py" | awk 'NR==1 {print $2}'`

