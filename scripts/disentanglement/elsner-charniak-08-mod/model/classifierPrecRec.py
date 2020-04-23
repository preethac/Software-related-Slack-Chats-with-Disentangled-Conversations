from __future__ import division
from sys import argv

from path import path
from StringIO import StringIO
from itertools import izip

from waterworks.Processes import bettersystem

import os

dirname = os.path.dirname(os.path.abspath(__file__))
megam = os.path.join(dirname, "../../elsner-charniak-08/megam_0.92/megam")

def score(predictions, feats):
    ffile = file(feats)
    preds = predictions.getvalue().rstrip().split("\n")

    right = 0
    lines = 0
    true1 = 0
    false1 = 0
    missed1 = 0

    for true, pred in izip(ffile, preds):
        truth = int(true.split(" ")[0])
        predLabel = int(pred.split("\t")[0])

        if truth == predLabel:
            right += 1
        if truth == 1 and predLabel == 1:
            true1 += 1
        elif predLabel == 1:
            false1 += 1
        elif truth == 1:
            missed1 += 1
        lines += 1

    prec = 0
    if true1 + false1 > 0:
        prec = true1 / (true1 + false1)
    rec = true1 / (true1 + missed1)
    f = 0
    if prec + rec > 0:
        f = (2*prec*rec)/(prec+rec)

    err = (lines-right)/lines
    acc = 1 - err
    print "Acc", acc, "P", prec, "R", rec, "F", f

if __name__ == "__main__":
    blockdir = path(argv[1])

    model = blockdir/"model"
    feats = blockdir/"devfeats"

    predictions = StringIO()

    bettersystem(megam + " -predict " + model +
                 " -fvals binary " + feats, stdout=predictions,
                 stderr=StringIO())

    score(predictions, feats)
