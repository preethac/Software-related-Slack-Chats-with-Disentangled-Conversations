from sys import argv
from math import floor
import pickle
import re

from path import path

from analysis.chatStats import readChat

def grep(word, files, cache):
    if cache.has_key(word):
        return cache[word]
        
    for f in files:
        fh = file(f)
        for line in fh:
            if word in line:
                cache[word] = True
                return True

    cache[word] = False
    return False

def fpart(x):
    return x - floor(x)

def hasWebAddr(line):
    if "http://" in line or "www." in line:
        return True
    return False

def hasBigNumber(words):
    for word in words:
        if word.isdigit():
            num = float(word)
            if num > 10 or fpart(num) > 0:
                return True

    return False

def hasLinuxWord(comment, linuxWords):
    for word in re.split("\s+", comment.rest):
        modWord = word

        modWord = modWord.rstrip(".)`']>\":;,!?")
        modWord = modWord.lstrip("([<`\"'")

        if modWord in comment.mentioned:
            continue

        modWord = modWord.lower()

        if modWord is "":
            continue

        if "'" in modWord: #ecparser separates these
            continue

        if modWord in linuxWords:
            #print "**************Linux word", modWord
            return True
        
    return False

def techTerm(comment, linuxWords):
    if hasWebAddr(comment.rest):
        return True
    if hasBigNumber(comment.words()):
        return True
    if hasLinuxWord(comment, linuxWords):
        return True    

if __name__ == "__main__":
    chat = readChat(argv[1])
    linuxWords = pickle.load(file(argv[2]))

#    for word in linuxWords:
#        print word

    for comment in chat:
        if techTerm(comment, linuxWords):
            print "\t\t", comment
        else:
            print comment
