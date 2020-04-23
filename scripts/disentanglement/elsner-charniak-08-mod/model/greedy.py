from analysis.chatStats import *

def resolve(currComment, votes, nextThread):
    maxScore = 0
    maxThread = -1
    
    for thread, score in votes.items():
        if score > maxScore:
            maxScore = score
            maxThread = thread

    if maxScore > 0:
#        print "Old"
        currComment.thread = maxThread
    else:
#        print "New"
        currComment.thread = nextThread
        nextThread += 1

#     print "Resolving", currComment
#     print votes
#     print currComment.thread
    
    return nextThread

if __name__ == "__main__":
    chat = readChat(argv[1])
    predictions = file(argv[2])
    keys = file(argv[3])

    copy = copyChat(chat)
    copy = blocks(copy, 1)

    objective = 0
    currI = -1
    votes = DefaultDict(0)
    nextThread = 2
    
    for predictionLine, keyLine, in izip(predictions, keys):
        prob = float(predictionLine.split()[1])
        (i, j) = map(int, keyLine.split())

        if i != currI:
            if currI > -1:
                currComment = copy[currI]
                nextThread = resolve(currComment, votes, nextThread)
                #print "Next thread now", nextThread

                for thread, vote in votes.items():
                    if thread == currComment.thread:
                        objective += vote
                    else:
                        objective -= vote
            
            currI = i
            votes = DefaultDict(0)

        assert(copy[j].thread != -1)
        votes[copy[j].thread] += prob - .5
        #print i, "prev comment", j, "voting for",\
        #    copy[j].thread, "with weight", (prob-.5)

    for x in copy:
        print x.readerStr()

#    print "Objective:", objective
#
#    describe(copy)
#    evaluate(chat, copy, "human", "system")
