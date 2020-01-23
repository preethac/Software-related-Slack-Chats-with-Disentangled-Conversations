import sys
import os
import numpy
from sklearn.ensemble import RandomForestClassifier
from imblearn.combine import SMOTETomek
from imblearn.over_sampling import SMOTE


def parseFeatureTypes(modelfile):
    feattypes = list()
    with open(modelfile, 'r') as f:
        for line in f:
            if not line.isspace() and not line.startswith("*"):
                parts = line.split(' ')
                feattypes.append(parts[0])
    return feattypes


def parseFeaturesFile(featfile, feattypes):
    labels = []
    features = []
    with open(featfile, 'r') as f:
        for line in f:
            if not line.isspace():
                parts = line.split(' ')
                labels.append(int(parts[0]))
                f_line = numpy.zeros(len(feattypes))
                for i in range(1,len(parts),2):
                    if(parts[i] in feattypes):
                        f_line[feattypes.index(parts[i])] = 1
                features.append(f_line)
    return features, labels


def printPredictions(predfile, proba):
    with open(predfile, 'w') as f:
        for pr_tuple in proba:
            if(pr_tuple[0] > 0.5):
                f.write("0\t" + str(1-pr_tuple[0]) + "\n")
            else:
                f.write("1\t" + str(pr_tuple[1]) + "\n")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("\tExample:\tpython doRandomForest.py output_dir")
        sys.exit()

    dirname = os.path.dirname(os.path.abspath(__file__))
    featfile = os.path.join(sys.argv[1],'feats')
    modelfile = os.path.join(dirname,'sample_model')
    assert(os.path.exists(featfile))
    assert(os.path.exists(modelfile))

    feattypes = parseFeatureTypes(modelfile)
    features, labels = parseFeaturesFile(featfile, feattypes)
    clf = RandomForestClassifier(n_estimators=500)
    #sm = SMOTETomek()
    sm = SMOTE()
    features_resampled, labels_resampled = sm.fit_sample(features, labels)
    clf = clf.fit(features_resampled, labels_resampled)
    #print(clf.feature_importances_)

    testfeatfile = os.path.join(sys.argv[1],'devfeats')
    assert(os.path.exists(testfeatfile))
    t_features, t_labels = parseFeaturesFile(testfeatfile, feattypes)
    t_proba = clf.predict_proba(t_features)
    #print(t_proba)

    testfeatfile = os.path.join(sys.argv[1],'predictions')
    printPredictions(testfeatfile,t_proba)
