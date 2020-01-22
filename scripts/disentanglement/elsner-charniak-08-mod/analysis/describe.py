from chatStats import *
from sys import argv

stats = {}
stats["threads"] = []
stats["avgSize"] = []
stats["avgDens"] = []
stats["entropy"] = []

def getStats(chat):
    ts = len(threadSizes(chat))
    av = avgSize(chat)
    dens = lineAvgThreads(chat)
    h = entropy(chat)

    stats["threads"].append(ts)
    stats["avgSize"].append(av)
    stats["avgDens"].append(dens)
    stats["entropy"].append(h)

for fname in argv[1:]:
    print fname
    chat = [x for x in readChat(fname)]

    getStats(chat)

for stat,lst in stats.items():
    print stat
    print "Max", max(lst)
    print "Min", min(lst)
    print "Avg", (sum(lst)/float(len(lst)))
