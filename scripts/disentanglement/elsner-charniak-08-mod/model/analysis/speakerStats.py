#!/usr/bin/env python
from __future__ import division

from AIMA import DefaultDict

import pylab

from chatStats import *

chat = nonSys(markSys(readChat(argv[1])))

print "Length is", len(chat)
spkLines = speakerLines(chat)
print "Speakers", len(spkLines)
print "Average utterances", avgUtterances(chat)
print "Average conversations", avgConversations(chat)

spkThreads = DefaultDict([])
for spk,lines in spkLines.items():
    spkThreads[spk] = [x.thread for x in lines]

#print spkThreads

utts= []
unique = []
for threads in spkThreads.values():
    utts.append(len(threads))
    unique.append(len(Set(threads)))

#print " ".join([str(x) for x in utts])
#print
#print " ".join([str(x) for x in unique])

pylab.xlabel("Utterances")
pylab.ylabel("Threads")
pylab.scatter(utts, unique, c='k')
pylab.yticks(range(11))
pylab.xlim(0, 65)
pylab.show()
