from analysis.chatStats import *
from techTerm import techTerm

from pickle import load, dump
from math import log
from sys import stderr

###############################
### KOSTA ADDED THIS BELOW: ###

def emoji(prev, curr, feats):
    for emoji in ["_+1_", "_bulb_", "_confetti_ball_", "_taco_"]:
        if emoji in prev.words():
            feats["prev_thx_emoji"] = 1
        if emoji in curr.words():
            feats["curr_thx_emoji"] = 1


def thx_for_answering(prev, curr, feats):
    for ans_word in ["got it", "gotcha", "makes sense", "makes perfect sense", "this works", "that works",
                     "that worked", "seems reasonable"]:
        ls1 = [element for element in ans_word.split() if element in prev.words()]
        ls2 = [element for element in prev.words() if element in ans_word.split()]
        if len(ls1) > 0 and ls1 == ls2:
            feats["prev_thx_for_answer"] = 1
        ls1 = [element for element in ans_word.split() if element in curr.words()]
        ls2 = [element for element in curr.words() if element in ans_word.split()]
        if len(ls1) > 0 and ls1 == ls2:
            feats["curr_thx_for_answer"] = 1

def code_block(prev, curr, feats):
    if "C" in prev.discType():
        feats['prev_code'] = 1
    if "C" in curr.discType():
        feats['curr_code'] = 1

def url(prev, curr, feats):
    if "U" in prev.discType():
        feats['prev_url'] = 1
    if "U" in curr.discType():
        feats['curr_url'] = 1

def channel(prev, curr, feats):
    if "#" in prev.discType():
        feats['prev_channel'] = 1
    if "#" in curr.discType():
        feats['curr_channel'] = 1

def fancy_question(prev, curr, feats):
    if "?" in curr.discType():
        feats["curr_q"] = 1
    if "?" in prev.discType():
        feats["prev_q"] = 1
    for qw in ['what','when','who','why','which','how','whose']:
        if qw in curr.words():
            feats["curr_q"] = 1
        if qw in prev.words():
            feats["prev_q"] = 1
    # for qw in ['can you', 'can someone', 'can anyone', 'is someone', 'is anyone', 'does someone', 'does anyone']:
    #     ls1 = [element for element in qw.split() if element in prev.words()]
    #     ls2 = [element for element in prev.words() if element in qw.split()]
    #     if len(ls1) > 0 and ls1 == ls2:
    #         feats["prev_q"] = 1
    #     ls1 = [element for element in qw.split() if element in curr.words()]
    #     ls2 = [element for element in curr.words() if element in qw.split()]
    #     if len(ls1) > 0 and ls1 == ls2:
    #         feats["curr_q"] = 1

speaker_time = DefaultDict(0)

def new_spkr(prev, curr, feats):
    feats["new_spkr"] = 1
    if curr.name in speaker_time.keys():
        time_since_spk = curr.time - speaker_time[curr.name]
        if time_since_spk > 0 and time_since_spk <= (60 * 60 * 1):
            feats["new_spkr"] = 0
    speaker_time[curr.name] = curr.time


### END OF KOSTA ADDED THIS ###
###############################



def repeatWord(prev, curr, feats):
    for prevWord in prev.words():
        for currWord in curr.words():
            if prevWord == currWord:
                wp = unigramProb[prevWord]
                if wp > 0:
                    #print "Word repeats", prevWord, wp
                    bin = -int(log(wp, 10))
                    ftype = "repeat_%d" % bin
                    #print ftype
                    feats[ftype] += 1
                ### KOSTA ADDED THIS BELOW: ###
                # forcing repeat_N to be computed even when the term doesn't exist in unigram pile
                else:
                    feats["repeat_1"] += 1


def greet(prev, curr, feats):
    if "G" in curr.discType():
        feats["curr_greet"] = 1
    if "G" in prev.discType():
        feats["prev_greet"] = 1

def answerWord(prev, curr, feats):
    for answer in ["yes", "yeah", "ok", "no", "nope"]:
        if answer in prev.words():
            feats["prev_answer"] = 1
        if answer in curr.words():
            feats["curr_answer"] = 1

def thanks(prev, curr, feats):
    for thx in ["thank", "thanks", "thx"]:
        if thx in prev.words():
            feats["prev_thx"] = 1
        if thx in curr.words():
            feats["curr_thx"] = 1

def question(prev, curr, feats):
    if "?" in curr.discType():
        feats["curr_q"] = 1
    if "?" in prev.discType():
        feats["prev_q"] = 1

def speaker(prev, curr, feats):
    if prev.name == curr.name:
        feats["same_spk"] = 1

def mention(prev, curr, feats):
    if prev.name in curr.mentioned:
        feats["prev_mentions_curr"] = 1
    if curr.name in prev.mentioned:
        feats["curr_mentions_prev"] = 1
    for ment in prev.mentioned:
        if ment in curr.mentioned:
            feats["same_mention"] = 1
    if prev.mentioned:
        feats["prev_mentions"] = 1
    if curr.mentioned:
        feats["curr_mentions"] = 1

def length(prev, curr, feats):
    if "L" in curr.discType():
        feats["curr_long"] = 1
    if "L" in prev.discType():
        feats["prev_long"] = 1

def deltaT(prev, curr, feats):
    dt = curr.time - prev.time

    bin = int(log(dt+1, 1.5))
    ftype = "dt_%d" % bin
    feats[ftype] = 1

def hasTech(prev, curr, feats):
    techPrev = techTerm(prev, linuxWords)
    techCurr = techTerm(curr, linuxWords)

    if techPrev and techCurr:
        feats["both_tech"] = 1
    elif techPrev or techCurr:
        feats["one_tech"] = 1
    else:
        feats["neither_tech"] = 1

#useless!
def multiDisc(prev, curr, feats):
    prevDisc = False
    for feat in ("prev_thx", "prev_greet", "prev_answer"):
        if feats.has_key(feat):
            prevDisc = True

    currDisc = False
    for feat in ("curr_thx", "curr_greet", "curr_answer"):
        if feats.has_key(feat):
            currDisc = True

    if prevDisc and currDisc:
        feats["both_disc"] = True

def squareFeats(feats):
   newFeats = DefaultDict(0)

   for feat, val in feats.items():
       for feat2, val2 in feats.items():
           if feat != feat2:
               newFeats[feat + "_"+feat2] = val*val2

   return newFeats

def pairFeats(prev, curr, output=None):
    feats = DefaultDict(0)
    same = prev.thread == curr.thread

    ###Kosta:
    fSet = [repeatWord, greet, answerWord, thanks, fancy_question,
            speaker, mention, length, deltaT, hasTech,
            emoji, thx_for_answering, code_block, url, channel] 

#, new_spkr]

#    fSet = [repeatWord, greet, answerWord, thanks, question,
#            speaker, mention, length, deltaT, hasTech]

#    fSet = [repeatWord, greet, answerWord, thanks, question,
#            speaker, length, deltaT, hasTech]

#    fSet = [deltaT, mention]

    #fSet = [deltaT, mention, speaker]
    #fSet = [greet, answerWord, thanks, question, length]
    #fSet = [repeatWord, hasTech]

    for feat in fSet:
        feat(prev, curr, feats)

    #feats = squareFeats(feats)

    if same:
        print >>output, "1",
    else:
        print >>output, "0",

    for feat, val in feats.items():
        print >>output, ("%s %f" % (feat, val)),

    print >>output

def timeSpanFeats(chat, logfile=None, blocksize=30, output=None):
    for currLine, curr in enumerate(chat):
        if curr.thread != -1:
            assert(curr.thread > 0)
            
            for prevLine, prev in enumerate(chat):
                if prev is curr:
                    break
                elif prev.thread == -1:
                    continue
                elif curr.time - prev.time < blocksize:
                    pairFeats(prev, curr, output)
                    logfile.write("%d %d\n" % (currLine, prevLine))
                ### KOSTA ADDED THIS BELOW: ###
                # forcing all recent pairs to be examined regardless of timespan
                elif (currLine - prevLine) <= 5:
                    pairFeats(prev, curr, output)
                    logfile.write("%d %d\n" % (currLine, prevLine))
		

def majority(chat, blocksize=30):
    lines = 0
    same = 0
    for currLine, curr in enumerate(chat):
        if curr.thread != -1:
            assert(curr.thread > 0)
            
            for prevLine, prev in enumerate(chat):
                if prev is curr:
                    break
                elif prev.thread == -1:
                    continue
                elif curr.time - prev.time < blocksize:
                    lines += 1
                    if prev.thread == curr.thread:
                        same += 1

    if same > lines/2:
        return 1
    else:
        return 0

def allMajority(chat, blocksize=30):
    maj = majority(chat, blocksize)
    right = 0
    lines = 0

    for currLine, curr in enumerate(chat):
        if curr.thread != -1:
            assert(curr.thread > 0)
            
            for prevLine, prev in enumerate(chat):
                if prev is curr:
                    break
                elif prev.thread == -1:
                    continue
                elif curr.time - prev.time < blocksize:
                    lines += 1
                    if prev.thread == curr.thread and maj == 1:
                        right += 1
                    elif prev.thread != curr.thread and maj == 0:
                        right += 1

    return float(right)/lines                        

if __name__ == "__main__":
    chat = readChat(argv[1])

    unigramModelFile = file(argv[2])
    stopWords = load(unigramModelFile)
    unigramProb = load(unigramModelFile)
    tot = load(unigramModelFile)
    tot = float(tot)

    for w in unigramProb:
        unigramProb[w] /= tot

    linuxWords = load(file("techwords.dump"))

    logfile = file(argv[3], 'w')

    blocksize = 200
    if len(argv) > 4:
        blocksize = int(argv[4])
    print >>stderr, "Blocksize:", blocksize
    
    timeSpanFeats(chat, logfile=logfile, blocksize=blocksize)
    logfile.close()
