import xml.etree.ElementTree as ET
import sys
import re
import string
from datetime import datetime

# load file
if len(sys.argv) < 3:
	print("Error: not enough parameters")
	print("\tFor example:\tpython revert_preprocessing.py disentagled_chat.txt original_chat.xml output_file")
	sys.exit()
disentagled_chat = sys.argv[1]
original_chat = sys.argv[2]
output_fname = sys.argv[3]

with open(disentagled_chat, 'r') as f:
	annotations = [x.split()[:3] for x in f.readlines()]

with open(original_chat, 'r', encoding='utf-8') as f:
	content = f.read()
root = ET.fromstring(content)

# first 4 elements are the team, channel, start date/time, and end date/time
info = root[:4]
messages = root[4:]

#remove empty text messages (since the preprocessing script does)
messages = [node for node in messages if node[-1].text != None]

# format input
TSfmt = '%Y-%m-%dT%H:%M:%S.%f'	# 24-hour time format
starttime = datetime.strptime(messages[0][0].text, TSfmt)
outputStr = ""
print("Total messages: " + str(len(messages)) + "\n", file=sys.stderr)
for node, annot in zip(messages, annotations):
	timestamp = node[0].text
	tdelta = datetime.strptime(timestamp, TSfmt) - starttime
	secondsFromStart = round(tdelta.total_seconds())

	#print(str(secondsFromStart) +  " " + str(annot[1]) + " " + timestamp)
	assert(secondsFromStart == int(annot[1]))

	#node.set('speaker_name', annot[2])
	node.set('conversation_id', annot[0][1:])


with open(output_fname, 'w') as f:
	f.write(ET.tostring(root,encoding="utf-8",method="xml").decode('utf-8'))

