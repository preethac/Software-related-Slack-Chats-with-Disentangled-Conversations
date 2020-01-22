#!/usr/bin/env python
from __future__ import division

import getopt
from chatStats import *
from distMat import getMetric
import sys
from pickle import load

def avg(list):
    return sum(list)/len(list)

def search(annotator, scoreFn, metric):
    bestScore = 0
    best = None

    for blocksize in range(10, 300, 5):
        #print blocksize
        base = annotator(copyChat(chat), blocksize)
        score = scoreFn([metric(base, x) for x in allChats])

        #print score

        if score > bestScore:
            bestScore = score
            best = blocksize

    print "Best %s annotation" % annotator.__name__, best, " score", bestScore

if __name__ == "__main__":
    keywords,args = getopt.getopt(sys.argv[1:], [], ["metric=", "score=",
                                                       "annotator="])

    keywords = dict(keywords)

    metric = getMetric(keywords)

    if not metric:
        print "Must use --metric [metric]!"
        sys.exit(1)

    scoreFn = keywords["--score"]
    if scoreFn == "min":
        scoreFn = min
    elif scoreFn == "max":
        scoreFn = max
    elif scoreFn == "avg":
        scoreFn = avg
    else:
        print "Need --score [min/max/avg]"
        sys.exit(1)

    annotator = keywords["--annotator"]
    if annotator == "blocks":
        annotator = blocks
    elif annotator == "pause":
        annotator = timeBreak
    elif scoreFn == "seconds":
        annotator = timeBreak
    else:
        print "Need --annotator [blocks/pause]"
        sys.exit(1)

    chat = [x for x in readChat(args[1])]

    allChats = []

    for annot in args[1:]:
        if annot.endswith(".annot"):
            print "Human transcript:", annot
            human = [x for x in readChat(annot)]
            allChats.append(human)
        else:
            raise TypeError("Need a .annot file, got %s" % annot)

    search(annotator, scoreFn, metric)
