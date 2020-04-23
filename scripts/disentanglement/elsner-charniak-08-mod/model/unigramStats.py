#!/usr/bin/env python

from sys import argv
import re
from pickle import load, dump

from chatStats import *

def getUnigrams(chat, stopWords = Set()):
    unigrams = DefaultDict(0)
    tot = 0
    
    for comment in markedSys(chat):
        if comment.thread > -1:
            for word in comment.words():
                if word not in stopWords:
                    unigrams[word] += 1
                    tot += 1

    return (unigrams, tot)

chat = readChat(argv[1])
(unigrams, tot) = getUnigrams(chat)
ugitems = unigrams.items()
ugitems.sort(lambda x, y: cmp(x[1], y[1]))
ugitems.reverse()
print list(enumerate(ugitems))
stopWords = Set(map(lambda x: x[0], ugitems[0:50]))

(unigrams, tot) = getUnigrams(chat, stopWords=stopWords)

# print unigrams
# print tot

fout = file(argv[2], 'w')
dump(stopWords, fout)
dump(unigrams, fout)
dump(tot, fout)

