import conditionalFeatures
from analysis.chatStats import readChat

from pickle import load
from sys import argv
from math import log, exp

from path import path
from StringIO import StringIO

from waterworks.Processes import bettersystem

import os

dirname = os.path.dirname(os.path.abspath(__file__))
megam = os.path.join(dirname, "../../elsner-charniak-08/megam_0.92/megam")

def lastLine(io):
    string = io.getvalue()
    string = string.rstrip().split("\n")
    return string[-1]

if __name__ == "__main__":
    train = readChat(argv[1])
    dev = readChat(argv[2])

    unigramModelFile = file(argv[3])
    stopWords = load(unigramModelFile)
    unigramProb = load(unigramModelFile)
    tot = load(unigramModelFile)
    tot = float(tot)

    for w in unigramProb:
        unigramProb[w] /= tot

    conditionalFeatures.unigramProb = unigramProb

    conditionalFeatures.linuxWords = load(file(argv[4]))

    basename = argv[5]

    basePath = path(basename)
    if not basePath.exists():
        basePath.mkdir()

    #this line controls how many block sizes are tried...
    for i in [18]: #range(1,18):
        blocksize = int(1.5**i)
        print "Blocksize", blocksize
        modeldir = basePath/str(blocksize)
        modeldir.mkdir()

        log = file(modeldir/"keys", 'w')
        feats = file(modeldir/"feats", 'w')

        conditionalFeatures.timeSpanFeats(train,
                                          logfile=log, blocksize=blocksize,
                                          output=feats)

        log.close()
        feats.close()

        devlog = file(modeldir/"devkeys", 'w')
        devfeats = file(modeldir/"devfeats", 'w')

        conditionalFeatures.timeSpanFeats(dev,
                                          logfile=devlog, blocksize=blocksize,
                                          output=devfeats)

        devlog.close()
        devfeats.close()        

        trainErr = StringIO()
        
        bettersystem(megam + " -fvals binary " + modeldir/"feats" +
                     " > " + modeldir/"model", stderr=trainErr)

        testErr = StringIO()

        bettersystem(megam + " -predict " + modeldir/"model"
                     " -fvals binary " + modeldir/"devfeats" +
                     "> " + modeldir/"predictions", stderr=testErr)

        trainErrStr = lastLine(trainErr)
        testErrStr = lastLine(testErr)

        print "Blocksize", blocksize, \
              "train err", trainErrStr, "test err", testErrStr
        print "Majority baseline error", \
              (1-conditionalFeatures.allMajority(dev, blocksize=blocksize))
        print
