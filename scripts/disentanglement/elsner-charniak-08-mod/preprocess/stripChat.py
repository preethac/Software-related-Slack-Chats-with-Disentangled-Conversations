#!/usr/bin/env python

#converts a gaim chatlog to a more ethical anonymized version
#format of the output is
#timestamp name : comment
#or
#timestamp name * action

from random import shuffle
from sys import argv
import re
from time import *

def timeToSecs(timeStr, prevTime):
    timeTuple = strptime(timeStr, "%H:%M:%S")
    (hr,min,sec) = timeTuple[3:6]
    totSecs = hr*60*60 + min*60 + sec
    diff = totSecs - prevTime
    while diff < 0:
        #keep incrementing by a day until we pass the prev time
        totSecs += 60*60*24
        diff = totSecs - prevTime
    return totSecs

#read the names list (got from the US census and preprocessed a little bit)
nameFile = "data/names"
names = [x.rstrip().title() for x in file(nameFile).readlines()]
shuffle(names)

#load up the file
chatFile = argv[1]
chat = file(chatFile)

print "Processing", chatFile

aliases = {}

#the intro line (my name, server id, true start time)
intro = chat.readline()
trueTime = re.search("at \S+ ([\d:]+)", intro)
assert(trueTime)
trueTime = timeToSecs(trueTime.group(1), 0)

channelName = re.search("Conversation with (\S+)", intro)
assert(channelName)
channelName = channelName.group(1)
aliases[channelName] = channelName

epoch = trueTime

basicRE = re.compile("\(([^)]+)\) ([^\s:]+)(:?)(.*)")

for line in chat:
    match = basicRE.match(line)
    assert(match)
    (time, name, comment, rest) = match.groups()

    trueTime = timeToSecs(time, trueTime)
    fakeTime = trueTime - epoch

    try:
        alias = aliases[name]
    except KeyError:
        alias = names.pop()
        aliases[name] = alias

    if "is now known as" not in rest:
        #obnoxiously, people can readopt others' nicknames
        #and then you get cross-aliasing
        for name in aliases.keys():
            if name in rest:
                namepatt = re.compile("(^|[^a-zA-Z]+)%s([^a-zA-Z]+|$)" %
                                       re.escape(name))
                if re.search(namepatt, rest):
                    rest = re.sub(namepatt, r"\1%s\2" % aliases[name], rest)

    if comment is ":":
        print fakeTime, alias, ":", rest                
    else:
        if rest.endswith("entered the room."):
            #really [n=me@my-real-address] entered the room
            rest = " entered the room."
        elif "is now known as" in rest:
            newName = re.search("is now known as ([^\s:]+)", rest)
            assert(newName)
            newName = newName.group(1)
            aliases[newName] = alias
            rest = rest.replace(newName, alias)
        print fakeTime, alias, "*", rest
