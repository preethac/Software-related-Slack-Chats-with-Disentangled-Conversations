#!/usr/bin/env python

from chatStats import *
import sys
from pickle import load
import getopt

def getVI(one, two):
    return vi(one, two)

def getLoc(one, two):
    return localError(one, two, window=3)

def getEntM21(one, two):
    h1 = entropy(one)
    h2 = entropy(two)

    assert(len(nonSys(annotated(one))) == len(nonSys(annotated(two))))
    assert(len(nonSys(annotated(one))) > 0)

    if h2 > h1:        
        cm = ConfusionMatrix()
        for gold,proposed in zip(nonSys(annotated(one)),
                                 nonSys(annotated(two))):
            cm.add(gold.thread, proposed.thread)

        return cm.eval_mapping(cm.many_to_one_mapping(), verbose=False)[2]
    else:
        cm = ConfusionMatrix()
        for gold,proposed in zip(nonSys(annotated(two)),
                                 nonSys(annotated(one))):
            cm.add(gold.thread, proposed.thread)

        return cm.eval_mapping(cm.many_to_one_mapping(), verbose=False)[2]

def isAll1(one):
    for x in nonSys(annotated(one)):
        if x.thread != 1:
            return False
    return True

def isAllDiff(one):
    ts = threadSizes(one)
    if len(ts) == len(nonSys(annotated(one))):
        return True
    return False

def get121(one, two):
    if isAllDiff(one):
        #hungarian will be vslow
        #but real result is easy, namely,
        #1 sentence of overlap per cluster in the other clustering
        return float(len(threadSizes(two))) / len(threadSizes(one))
    elif isAllDiff(two):
        return float(len(threadSizes(one))) / len(threadSizes(two))
    
    cm = ConfusionMatrix()
    for gold,proposed in zip(nonSys(annotated(one)),
                             nonSys(annotated(two))):
        cm.add(gold.thread, proposed.thread)

    return cm.eval_mapping(cm.one_to_one_optimal_mapping(),
                           verbose=False)[2]

def getMetric(metricName):
    try:
        met = metricName["--metric"]
    except:
        return None        

    if met == "121":
        return get121
    elif met == "m21":
        return getEntM21
    elif met == "loc3":
        return getLoc
    elif met == "vi":
        return getVI
    else:
        raise KeyError("Unrecognized metric %s" % met)

if __name__ == "__main__":
    keywords,args = getopt.getopt(sys.argv[1:], [], ["metric="])
    keywords = dict(keywords)

    metric = getMetric(keywords)
    print "Metric", metric.__name__
    if not metric:
        print "Must use --metric [metric]!"
        sys.exit(1)

    chat = [x for x in readChat(args[1])]

    allChats = []

    for annot in args[1:]:
        if annot == "speaker":
            print "speaker"
            allChats.append(singleSpeaker(copyChat(chat)))
        elif annot[0] == "b":
            num = int(annot[1:])
            print "blocks annotation", num
            allChats.append(blocks(copyChat(chat), num))
        elif annot[0] == "s":
            num = int(annot[1:])
            print "seconds annotation", num
            allChats.append(timeBreak(copyChat(chat), num))
        elif annot == "alldiff":
            print "all diff"
            allChats.append(blocks(copyChat(chat), 1))
        elif annot == "all1":
            print "all 1"
            allChats.append(allOne(copyChat(chat)))
        elif annot.endswith(".annot"):
            print "Human transcript:", annot
            human = [x for x in readChat(annot)]
            allChats.append(human)
        else:
            raise TypeError("Unknown file type: %s" % annot)

    ndists = len(allChats)
    distmat = []
    for i in allChats:
        distmat.append([0.0] * ndists)

    for i,annot in enumerate(allChats):
        for jp,annot2 in enumerate(allChats[i+1:]):
            j = jp + i+1

            dist = metric(annot, annot2)
            distmat[i][j] = dist
            distmat[j][i] = dist

    for row in distmat:
        for j in row:
            print j,
        print
