from datetime import datetime
import os.path

from lxml import etree

from muse.block import Block
from muse.paths import replace_ext


def convert_block_to_xml(path, block):
    root = etree.Element('slack')
    etree.SubElement(root, 'team_domain').text = block.data['team_domain']
    etree.SubElement(root, 'channel_name').text = block.data['channel_name']
    etree.SubElement(root, 'start_date').text = block.data['start_date']
    etree.SubElement(root, 'end_date').text = block.data['end_date']
    for message in reversed(block.children):
        data = message.data
        keys = data.keys()
        if 'user' not in keys:
            # e.g., if message has subtype 'file_comment' or 'bot_message'
            continue
        if 'subtype' in data.keys():
            subtype = data['subtype']
            if subtype in ['channel_join', 'channel_leave',
                           'file_share', 'slackbot_response',
                           'pinned_item', 'reply_broadcast',
                           'me_message']:
                continue
        ts = datetime.fromtimestamp(float(data['ts'])).isoformat('T')
        #message_element = etree.SubElement(root, 'message', ts=ts, user=data['user']).text = data['text']
        message_element = etree.SubElement(root, 'message')
        etree.SubElement(message_element, 'ts').text = ts
        etree.SubElement(message_element, 'user').text = data['user']
        try:
            etree.SubElement(message_element, 'text').text = data['text']
        except ValueError as ex:
            try:
                etree.SubElement(message_element, 'text').text = ''.join(c for c in data['text'] if is_valid_xml_char(c))
            except ValueError as ex:
                raise
    with open(replace_ext(path, '.xml'), 'w', encoding='utf-8') as xmlfile:
        print(etree.tostring(root, encoding='utf-8', pretty_print=True, xml_declaration=True).decode('utf-8'), file=xmlfile)


def main(args):
    if len(args) < 2:
        print('Usage: {0} PATH'.format(args[0]))
        return 1

    file_or_directory = args[1]
    if not os.path.exists(file_or_directory):
        print('PATH does not exist:', file_or_directory)
        return 2

    if os.path.isfile(file_or_directory):
        with open(file_or_directory, 'r') as f:
            convert_block_to_xml(file_or_directory, Block.from_json(f))
    elif os.path.isdir(file_or_directory):
        for path, block in Block.read_directory(file_or_directory):
            convert_block_to_xml(path, block)

    return 0


def is_valid_xml_char(char):
    codepoint = ord(char)
    return 0x20 <= codepoint <= 0xD7FF or \
            codepoint in (0x9, 0xA, 0xD) or \
            0xE000 <= codepoint <= 0xFFFD or \
            0x10000 <= codepoint <= 0x10FFFF


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

