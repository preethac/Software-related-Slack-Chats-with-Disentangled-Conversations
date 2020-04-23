# Software-related Slack Chats with Disentangled Conversations

## Overview

This repository contains Slack Q&A style conversations and code for disentangling conversations, as described in:

- P. Chaterjee, K. Damevski, N. Kraft, L. Pollock. "Software-related Slack Chats with Disentangled Conversations". _submitted_

#### Data Origin: 
Numerous public Slack chat channels (https://slack.com/) have recently become available that are focused on specific software engineering-related discussion topics, e.g., Python Development (https://pyslackers.com/web/slack). We call the channels in which participants are asking and answering questions, Slack Q&A channels.  The channels are advertised on the Web and allow anyone to join, with a joining process only requiring the participant to create a username (any unique string) and a password. Once joined, on these channels, participants can ask or answer any question, as long as it pertains to the main topic (e.g., programming in Python).  

#### Data Collection Process: 
For our research, we collect data in the form of whole conversations from several technology communities that are focused on getting help and learning about software-related topics, specifically on using the following technologies: python, clojure, elm, and racket. To gather and store the conversations from each of the targeted Slack Q&A channels, we asked for permission from the channel administrators by sending them a direct message via the Slack platform stating who we are and our purpose (i.e., software engineering research). Those administrators who agreed then granted us a special Slack token, which we use to collect the daily channel activity. 

## Data Format

The Slack data is in XML format, with three attributes for each message: timestamp (_ts_), anonymized user id (_user_), and message _text_. The result of disentanglement, which groups utterances into conversations is provided as the _conversation_id_ attribute of each message.

```
 <message conversation_id="1">
    <ts>2017-06-16T10:51:34.290598</ts>
    <user>Kristie</user>
    <text>Is it possible to switch between conda and virtualenv? That is I want to switch the actual environment managers not just environments in them … I typically use conda but want to try something out that requires virtual env and is not compatible with conda.  Thanks.</text>
  </message>
  <message conversation_id="1">
    <ts>2017-06-16T10:55:34.384740</ts>
    <user>Glennis</user>
    <text>What is it that "requires virtualenv", most things I know don't require anything other than an interpreter and dependencies</text>
  </message>
  <message conversation_id="1">
    <ts>2017-06-16T11:05:27.626658</ts>
    <user>Kristie</user>
    <text>&lt;@Glennis&gt; zappa …. at least if you don’t want to mess with the zappa-conda fork.</text>
  </message>
  <message conversation_id="1">
    <ts>2017-06-16T11:12:26.790435</ts>
    <user>Glory</user>
    <text>i don’t see why you couldn’t use a virtualenv for virtualenv things and conda for conda things. the issue is when you try to mix them together but as long as you’re pointed at the right python interpreter things should work.</text>
  </message>
```

Our dataset consists of approximately two years of activity between mid 2017 (varies slightly by channel) and mid 2019 (June 6th, 2019) from 5 Slack channels (_pythondev-help_, _clojurians-clojure_, _elmlang-beginners_, _elmlang-general_, and _racket-general_), representing 4 Slack communities (_clojurians_, _pythondev_, _elmlang_, and _racket_):

```
data
+-- clojurians
|   +-- 2017
|   |   +--- merged-clojurians-clojure.xml
|   +-- 2018
|   |   +--- merged-clojurians-clojure.xml
|   +-- 2019
|   |   +--- merged-clojurians-clojure.xml
+-- pythondev
|   +-- ...
+-- elmlang
|   +-- ...
+-- racket
|   +-- ...
```

## Slack Scripts

We provide scripts we used for processing the downloaded data from the orginal Slack JSON format we downloaded to the simplified XML format that contains only the utterances. These scripts are in the `scripts/slack` directory

## Disentanglement

Disentanglement scripts (based on Elsner and Charniak's prior work) are included in the `scripts/disentanglement` directory. Running
the *run_distantanglement.sh* shell script disentangles the XML data files. The bash script
invokes Elsner and Charniak's code (with our minor modifications detailed below) as well as some of our own pre- and post-processing.


**Resources for Elsner and Charniak, 2008**
+ https://www.asc.ohio-state.edu/elsner.14/resources/chat-distr.tgz
+ https://www.asc.ohio-state.edu/elsner.14/resources/chat-manual.html
+ http://aclweb.org/anthology-new/J/J10/J10-3004.pdf

**List of our modifications to Elsner and Charniak**
+ changed block size from 1.5^12 to 1.5^18 
+ forced to evaluate last 5 messages regardless of timespan
+ added random forest (E&C used maximum entropy) classification for portability as results were similar
+ changed and added features, including new Slack-specific features:

1. Cue Words (Q&A conversations sometimes end with gratitude):
    + prev_thx_for_answer -- e.g., "got it", "gotcha", "makes sense", "makes perfect sense", "this works", "that works", "that worked", "seems reasonable"
    + curr_thx_for_answer
2. Code:
    + prev_code -- starts/ends with ```
    + current_code 
3. URL (answers to development related questions can be URLs):
    + prev_url
    + curr_url
4. Channel (mentions #channel in message if a message is inappropriate for the current channel):
    + prev_channel  
    + curr_channel
5. *Changed* Repeat (repeated words, weighted unigram file of (term, frequency) and k is computed as log(frequency, base=10); (new) include influence for repeated words that don't exist in the precomputed list of unigrams):
    + repeat_k  
5. *Changed* Question (existence of the '?' symbol; (new) enhanced to include the wh words):
    + curr_q 
    + prev_q
