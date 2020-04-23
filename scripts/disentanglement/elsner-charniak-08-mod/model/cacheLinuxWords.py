from path import path
from sets import Set
import sre
from sys import argv
from pickle import dump

from InputTree import InputTree

def cacheText(files, cache):
    for f in files:
        fh = file(f)
        for line in fh:
            for word in sre.split("\s+", line):
                modWord = word.lower()
                modWord = modWord.rstrip(".)`']>\":;,!?")
                modWord = modWord.lstrip("([<`\"':")

                if "http://" in modWord:
                    continue

                if len(modWord) < 2:
                    continue

                #print modWord
                cache.add(modWord)

def removeTreeWords(files, cache):
    for f in files:
        fh = file(f)
        for line in fh:
            t = InputTree(line)            
            for word in t.getYield():
                cache.discard(word)

if __name__ == "__main__":
    techWords = Set()

    linuxFiles = path(argv[1]).files()
    linuxFiles = filter(lambda x : x.endswith(".txt"), linuxFiles)
    journalFiles = path(argv[2]).files()

    print "Reading linux texts..."
    cacheText(linuxFiles, techWords)
    print "Reading news..."
    removeTreeWords(journalFiles, techWords)

    print "Dumping now..."
    out = file(argv[3], 'w')
    dump(techWords, out)
    out.close()
    #print techWords
