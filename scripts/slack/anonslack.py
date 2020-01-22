import xml.etree.ElementTree as ET
import sys
import re
from random import shuffle
from datetime import datetime


def replaceMentions(text, aliasDict):
	text = str(text)
	mentionPattern = '<@U\w+>'
	while re.search(mentionPattern,text):
		indexStart = re.search(mentionPattern,text).span()[0]
		indexEnd = re.search(mentionPattern,text).span()[1]
		mentionName = text[indexStart+2:indexEnd-1]
		try:
			mentionAlias = aliasDict[mentionName]
		except KeyError:
			aliasDict[mentionName] = names.pop()
			mentionAlias = aliasDict[mentionName]
		text = text[:indexStart] + "<@" + mentionAlias + ">"+ text[indexEnd:]
	return text

# load file
if len(sys.argv) < 3:
	print("Error: not enough parameters")
	print("\tFor example:\tpython anonslack.py names_file original_chat.xml output_file")
	sys.exit()
names_file = sys.argv[1]
original_chat = sys.argv[2]
output_fname = sys.argv[3]


names = []
with open(names_file, 'r') as f:
	names = [x.rstrip().title() for x in f.readlines()]
shuffle(names)
aliasDict = {}

with open(original_chat, 'r', encoding='utf-8') as f:
	content = f.read()
root = ET.fromstring(content)

# first 4 elements are the team, channel, start date/time, and end date/time
info = root[:4]
nodes = root[4:]

# format input
TSfmt = '%Y-%m-%dT%H:%M:%S.%f'	# 24-hour time format
starttime = datetime.strptime(nodes[0][0].text, TSfmt)
outputStr = ""
print("Total messages: " + str(len(nodes)) + "\n", file=sys.stderr)
for node in nodes:
	timestamp = node[0].text
	tdelta = datetime.strptime(timestamp, TSfmt) - starttime
	secondsFromStart = round(tdelta.total_seconds())

	user = node[1].text
	text = node[-1].text

	alias = user
	try:
		alias = aliasDict[user]
	except KeyError:
		aliasDict[user] = names.pop()
		alias = aliasDict[user]

	node[1].text = alias
	node[-1].text = replaceMentions(text,aliasDict)


with open(output_fname, 'w') as f:
	f.write(ET.tostring(root,encoding="utf-8",method="xml").decode('utf-8'))

