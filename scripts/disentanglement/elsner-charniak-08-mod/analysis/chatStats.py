#!/usr/bin/env python

import os
import re
from sys import argv
from math import log, sqrt
from copy import copy
from sets import Set

from itertools import *
from AIMA import removeall, DefaultDict

from grouper import Grouper

from ClusterMetrics import ConfusionMatrix
# from scipy import array, zeros, dot

#######parse and read

basicRE = re.compile("(?:T(-?\d+) )?(\d+) (\S+) (:|\*)  (.*)");
getwords = re.compile("\W+")
emoji = re.compile(":(\w+):")

class Comment:
    def __init__(self, thread, time, name, comment, rest):
        if thread:
            self.thread = int(thread)
        else:
            self.thread = 0
        self.time = int(time)
        self.name = name

        if comment == ":":
            self.comment = True
        else:
            assert(comment == "*")
            self.comment = False

        ### KOSTA ADDED THIS BELOW: ###
        rest = emoji.sub("_\g<1>_", rest)

        self.rest = rest
        self.mentioned = []
        self.features = None

    def words(self):
        wds = re.split(getwords, self.rest.strip())
        for wd in self.mentioned:
            wds = removeall(wd, wds)
        wds = removeall("", wds)
        return [w.lower() for w in wds]

    def discType(self):
        isLong = len(self.words()) > 10
        hasChannel = re.search("#\w+", self.rest)
        hasCode = re.search("```|==BLOCK REMOVED==", self.rest)
        hasURL = re.search("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", self.rest)
        hasQ = "?" in self.rest

        hasGreet = False
        for greet in ["hey", "hi", "hello"]:
            if greet in self.words():
                hasGreet = True
                break

        res = ""
        if hasChannel:
            res += "#"
        if hasURL:
            res += "U"
        if hasCode:
            res += "C"
        if hasQ:
            res += "?"
        if hasGreet:
            res += "G"
        if isLong:
            res += "L"

        return res        

    def isSys(self):
        return self.rest.count("entered the room") or \
               self.rest.count("left the room") or \
               self.rest.count("mode (") or \
               self.rest.count("is now known as")

    def readerStr(self):
        comment = ":"
        if not self.comment:
            comment = "*"
        
        return "T%d %d %s %s  %s" % (self.thread, self.time, self.name,
                                    comment, self.rest)

    def __str__(self):
        comment = ":"
        if not self.comment:
            comment = ""

        return "T%d %d %s%s %s" % (self.thread, self.time,
                                   self.name, comment, self.rest)

def parseChat(line):
    #print '--' + line + '---'
    match = basicRE.match(line)
    assert(match)
    return Comment(*match.groups())

def readChat(filename):
    chat = [parseChat(l) for l in file(filename).readlines() if not l.isspace()]

    spkNames = {}

    for comment in chat:
        if not spkNames.has_key(comment.name):
            spkNames[comment.name] = re.compile(
                "(^|[^a-zA-Z]+)%s([^a-zA-Z]+|$)" % re.escape(comment.name))

        for otherSpk, otherRe in spkNames.items():
            if re.search(otherRe, comment.rest):
                comment.mentioned.append(otherSpk)

    return chat

def annotated(chat):
    return [x for x in takewhile(lambda(l): l.thread != 0, chat)]

def markSys(chat):
    return list(markedSys(chat))

def markedSys(chat):
    for line in chat:
        if line.isSys():
            line.thread = -1
        yield line

def nonSys(chat):
    return filter(lambda(l): l.thread != -1, chat)

######stats

def threads(chat):
    ids = [x.thread for x in chat]
    return removeall(-1, ids) #system thread doesn't count

def threadSizes(chat):
    ids = threads(chat)
    counts = DefaultDict(0)

    for t in ids:
        counts[t] += 1

    return counts

def log2(x):
    return log(x, 2)

def entropy(chat):
    sizes = threadSizes(chat)
    tot = sum(sizes.values()) + 0.0

    for t in sizes:
        sizes[t] /= tot

    ent = 0.0
    for prob in sizes.values():
        ent += prob * log2(prob)

    return -ent

#note: using this below yields an O(n^2) MI algorithm
def intersects(c1, c2, threads1, threads2):
    assert(len(threads1) == len(threads2))
    res = 0
    for i in range(len(threads1)):
        if threads1[i] == c1 and threads2[i] == c2:
           res += 1
    return res

def mi(chat1, chat2):
    sizes1 = threadSizes(chat1)
    sizes2 = threadSizes(chat2)

    threads1 = threads(chat1)
    threads2 = threads(chat2)
    assert(len(threads1) == len(threads2))
    nlines = (len(threads1) + 0.0)
    intersects = DefaultDict(DefaultDict(0))

    for t1, t2 in izip(threads1, threads2):
        intersects[t1][t2] += 1

    res = 0.0
    
    for k1 in sizes1:
        for k2 in sizes2:
            jointp = intersects[k1][k2] / nlines
            pk1 = sizes1[k1] / nlines
            pk2 = sizes2[k2] / nlines

            if jointp:
                term = jointp * log2(jointp / (pk1 * pk2))
            else:
                term = 0
                
            res += term

    return res

def vi(chat1, chat2):
    e1 = entropy(chat1)
    e2 = entropy(chat2)
    minf = mi(chat1, chat2)
    res = e1 + e2 - 2*minf
    return res

def avgSize(chat):
    sizes = threadSizes(chat)
    tot = len(sizes) + 0.0
    return sum([sz for sz in sizes.values()]) / tot

def medSize(chat):
    sizes = threadSizes(chat)
    sizes = sizes.values()
    sizes.sort()
    return sizes[len(sizes)/2]

def interruptions(thread, chat):
    ids = threads(chat)
    first = ids.index(thread)

    for x in range(first, len(ids)):
        if ids[x] == thread:
            last = x

    if first == last:
        return 0.0
    
    section = ids[first:last]

    others = removeall(thread, section)
    tSize = len(section) - len(others) + 0.0
    return len(others)/tSize

def avgInterruptions(chat):
    szs = threadSizes(chat)
    ints = 0.0

    for thread in szs:
        intsPer = interruptions(thread, chat)
        ints += intsPer

    return ints/len(szs)

def medInterruptions(chat):
    szs = threadSizes(chat)
    ints = []

    for thread in szs:
        intsPer = interruptions(thread, chat)
        ints.append(intsPer)

    ints.sort()
    return ints[len(ints)/2]

def lineAvgThreads(chat):
    lastLine = {}
    for line in nonSys(markedSys(chat)):
        lastLine[line.thread] = line    

    tsActive = Set()
    totalActive = 0.0
    lines = 0.0
    for line in nonSys(markedSys(chat)):
        lines += 1
        tsActive.add(line.thread)
        totalActive += len(tsActive)

        if lastLine[line.thread] == line:
            tsActive.remove(line.thread)

    return totalActive/lines

def threadsPerBlock(chat, block):
    ts = threads(chat)

    res = 0.0
    blocks = 0
    
    for i in range(len(ts)-block):
        sseq = ts[i:i+block];
        sscts = {}

        for tid in sseq:
            sscts[tid] = 1

        uniques = len(sscts)

        blocks += 1
        res += uniques

    if blocks == 0:
        return 0

    return res/blocks

def deltaTList(chat):
    currTs = {}

    deltaTs = []

    for comment in chat:
        if comment.thread > 0:
            if not currTs.has_key(comment.thread):
                currTs[comment.thread] = comment.time
            else:
                prevT = currTs[comment.thread]
                delta = comment.time - prevT
                deltaTs.append(delta)
                currTs[comment.thread] = comment.time

    return deltaTs

def printElapsedTime(chat):
    startT = chat[0].time
    endT = chat[-1].time
    secs = endT - startT
    mins = secs/60.0
    hrs = mins/60.0
    print "%d:%d:%d" % (int(hrs), int(mins%60), int(secs%60))

def wordsSpoken(line):
    return len(line.words())

def speakerLines(chat):
    spkToLines = DefaultDict([])
    for comment in chat:
        spkToLines[comment.name].append(comment)
    return spkToLines

def avgConversations(chat):
    spkToLines = speakerLines(chat)
    res = 0.0
    for lineSet in spkToLines.values():
        uniques = Set([x.thread for x in lineSet])
        res += len(uniques)
    return res/len(spkToLines)

def avgUtterances(chat):
    spkToLines = speakerLines(chat)
    res = 0.0
    for lineSet in spkToLines.values():
        res += len(lineSet)
    return res/len(spkToLines)

def localError(ref, test, window=1):
    #window is the one-sided size of the window
    right = 0
    wrong = 0

    #note that this strips the -1
    testTs = threads(test)
    goldTs = threads(ref)

    for center in range(window, len(testTs)):
        #print "Center", center
        goldCenter = goldTs[center]
        testCenter = testTs[center]

        for probe in range(-window,0):
            #print "Probe", probe
            #print goldTs[center+probe], goldCenter, \
            #      testTs[center+probe], testCenter

            if (goldTs[center+probe] == goldCenter) is \
                   (testTs[center+probe] == testCenter):
                right += 1
                #print "Right"
            else:
                wrong += 1
                #print "Wrong"

    if right == 0 and wrong == 0:
        return 0
    return float(right)/(right+wrong)

#########baselines

def copyChat(chat):
    return [copy(x) for x in chat]

def allOne(chat):
    for comment in chat:
        if comment.thread > 0:
            comment.thread = 1
    return chat

def blocks(chat, blocksize):
    ctr = 0
    block = 1
    for comment in chat:
        if comment.thread > 0:
            comment.thread = block
            ctr += 1

            if ctr >= blocksize:
                ctr = 0
                block += 1
    return chat

def contiguous(chat):
    ctr = 0
    prevthread = -1
    for comment in chat:
        if comment.thread > 0:
            if comment.thread == prevthread:
                comment.thread = ctr
            else:
                prevthread = comment.thread
                ctr += 1
                comment.thread = ctr
    return chat

def singleSpeaker(chat):
    speakers = {}
    for comment in chat:
        if comment.thread > 0:
            if speakers.has_key(comment.name):
                comment.thread = speakers[comment.name]
            else:
                newN = len(speakers) + 1
                speakers[comment.name] = newN
                comment.thread = newN
    return chat

def timeBreak(chat, gap):
    ctr = 0
    deltaT = gap+1
    prevT = -(gap+1)
    for comment in chat:
        if comment.thread > 0:
            deltaT = comment.time - prevT
            if deltaT > gap:
                ctr += 1
            prevT = comment.time
            comment.thread = ctr
    return chat

def mergedSpeakers(chat):
    gps = Grouper()

    for comment in chat:
        if comment.thread > 0:
            spkr = comment.name
            gps.join(comment.name, comment.name)
            for ment in comment.mentioned:
                gps.join(comment.name, ment)

    gpToNum = {}
    for ctr, gp in enumerate(gps):
        gpToNum[tuple(gp)] = ctr + 1

    for comment in chat:
        if comment.thread > 0:
            gp = gps.find(comment.name)
            num = gpToNum[tuple(gp)]
            comment.thread = num

    return chat

#########output

def describe(chat):
    aLines = [x for x in annotated(chat)]

    print "The annotated part of this transcript has", len(aLines), "lines."
    print "Non-system lines:", len(threads(aLines)), "."
    print len(threadSizes(aLines)), "unique threads."
    print "The average conversation length is", avgSize(aLines), "."
    print "The median conversation length is", medSize(aLines), "."
    print "The entropy is", entropy(aLines), "bits."
    print "The median chat has", medInterruptions(aLines), \
          "interruptions per line."
    block = 10
    print "The average block of", block, "contains", \
          threadsPerBlock(aLines, block), "threads."
    print "The line-averaged conversation density is ", \
          lineAvgThreads(aLines), "."
    print

def evaluate(ref, test, refName="", testName=""):
    if testName and refName:
        print "Evaluating", testName, "against", refName,

    cm = ConfusionMatrix()
    assert(len(nonSys(annotated(ref))) == len(nonSys(annotated(test))))
    assert(len(nonSys(annotated(ref))) > 0)
    for gold,proposed in zip(nonSys(annotated(ref)), nonSys(annotated(test))):
        cm.add(gold.thread, proposed.thread)

    print "VI:", cm.variation_of_information(),
    print "MI:", cm.mutual_information(),
    print "1-1-g:", cm.eval_mapping(cm.one_to_one_greedy_mapping(),
                                    verbose=False)[2],
    print "1-1-o:", cm.eval_mapping(cm.one_to_one_optimal_mapping(),
                                    verbose=False)[2],
    print "m-1:", cm.eval_mapping(cm.many_to_one_mapping(), verbose=False)[2],

    print "loc-1:", localError(ref, test, window=1),
    print "loc-2:", localError(ref, test, window=2),
    print "loc-3:", localError(ref, test, window=3)


def printchat(chat, filename):
    with open(filename, "w") as f:
        for x in chat:
            f.write(x.__str__() + "\n")


if __name__ == "__main__":
    chat = [x for x in readChat(argv[1])]

    print "Annotation:"
    describe(chat)

    print "Baseline all 1s:"
    all1 = allOne(copyChat(chat))
    describe(all1)

    print "Baseline all different:"
    allDiff = blocks(copyChat(chat), 1)
    describe(allDiff)

    print "Blocks of 10:"
    blocks10 = blocks(copyChat(chat), 10)
    describe(blocks10)

    print "Blocks of 20:"
    blocks20 = blocks(copyChat(chat), 20)
    describe(blocks20)

    print "Blocks of 50:"
    blocks50 = blocks(copyChat(chat), 50)
    describe(blocks50)

    print "Blocks of 100:"
    blocks100 = blocks(copyChat(chat), 100)
    describe(blocks100)

    print "Blocks of 200:"
    blocks200 = blocks(copyChat(chat), 200)
    describe(blocks200)

    print "Contiguous blocks from annotation:"
    contig = contiguous(copyChat(chat))
    describe(contig)

    print "One thread per speaker:"
    speaker = singleSpeaker(copyChat(chat))
    describe(speaker)

    print "Gaps of 10s:"
    s10 = timeBreak(copyChat(chat), 10)
    describe(s10)

    print "Gaps of 20s:"
    s20 = timeBreak(copyChat(chat), 20)
    describe(s20)

    print "Gaps of 30s:"
    s30 = timeBreak(copyChat(chat), 30)
    describe(s30)

    print "Gaps of 60s:"
    s60 = timeBreak(copyChat(chat), 60)
    describe(s60)

    print "Gaps of 90s:"
    s90 = timeBreak(copyChat(chat), 90)
    describe(s90)

    print "Gaps of 180s:"
    s180 = timeBreak(copyChat(chat), 180)
    describe(s180)

    print "Merged speakers:"
    mrg = mergedSpeakers(copyChat(chat))
    describe(mrg)

    print "Sanity check:", vi(annotated(allDiff), annotated(all1)), "."
    print "Log(n):", log2(len(threads(annotated(all1)))), ".\n"

    #evaluate(allDiff, all1)
    print "Done sanity checking.\n"

#    evaluate(chat, all1, "human", "all1")
#    evaluate(chat, allDiff, "human", "allDiff")
#    evaluate(chat, blocks10, "human", "blocks10")
#    evaluate(chat, blocks20, "human", "blocks20")
#    evaluate(chat, blocks50, "human", "blocks50")
#    evaluate(chat, blocks100, "human", "blocks100")
#    evaluate(chat, blocks200, "human", "blocks200")
#    evaluate(chat, contig, "human", "contiguous")
#    evaluate(chat, speaker, "human", "speaker")
#    evaluate(chat, s10, "human", "s10")
#    evaluate(chat, s20, "human", "s20")
#    evaluate(chat, s30, "human", "s30")
#    evaluate(chat, s60, "human", "s60")
#    evaluate(chat, s90, "human", "s90")
#    evaluate(chat, mrg, "human", "merged")

    outpath = argv[2]
    if(os.path.exists(outpath)):
        printchat(all1, os.path.join(outpath,'all1'))
        printchat(allDiff, os.path.join(outpath,'allDiff'))
        printchat(blocks10, os.path.join(outpath,'blocks10'))
        printchat(blocks20, os.path.join(outpath,'blocks20'))
        printchat(blocks50, os.path.join(outpath,'blocks50'))
        printchat(blocks100, os.path.join(outpath,'blocks100'))
        printchat(blocks100, os.path.join(outpath,'blocks200'))
        printchat(speaker, os.path.join(outpath,'speaker'))
        printchat(s10, os.path.join(outpath,'s10'))
        printchat(s20, os.path.join(outpath,'s20'))
        printchat(s30, os.path.join(outpath,'s30'))
        printchat(s60, os.path.join(outpath,'s60'))
        printchat(s90, os.path.join(outpath,'s90'))
        printchat(s90, os.path.join(outpath,'s180'))
