#!/usr/bin/env python

from chatStats import *
from sys import argv

for fname in argv[1:]:
    chat = readChat(fname)
    printElapsedTime(chat)
