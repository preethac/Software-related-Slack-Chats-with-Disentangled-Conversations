#!/usr/bin/env python
from __future__ import division

from chatStats import *
from sys import argv

chat = readChat(argv[1])

dts = deltaTList(chat)
dts.sort()

# covered = 0
# for i in range(len(dts)):
#     if i/len(dts) > .1+covered:
#         print dts[i], "covers", i/len(dts)
#         covered += .1

print dts
