from collections import deque
from datetime import datetime
import os.path

from muse.block import Block
from muse.paths import mkdir_p


def main(args):
    if len(args) < 2:
        print('Usage: {0} DIRECTORY'.format(args[0]))
        return 1
    directory = args[1]

    team_domain = None
    channel_name = None
    start_dates = set()
    end_dates = set()
    messages = dict()

    for path, block in Block.read_directory(directory):
        if team_domain is None:
            team_domain = block.data['team_domain']
        else:
            assert(team_domain == block.data['team_domain'])
        if channel_name is None:
            channel_name = block.data['channel_name']
        else:
            assert(channel_name == block.data['channel_name'])
        start_dates.add(block.data['start_date'])
        end_dates.add(block.data['end_date'])
        for message in block.children:
            ts = datetime.fromtimestamp(float(message.data['ts'])).isoformat('T')
            if ts not in messages:
                messages[ts] = message

    data = {'team_domain' : team_domain,
            'channel_name' : channel_name,
            'start_date' : sorted(start_dates)[0],
            'end_date' : sorted(end_dates)[-1]}
    children = deque()
    for ts in sorted(messages.keys()):
        children.appendleft(messages[ts])

    merged = Block(data, list(children))
    with open(os.path.join(directory, 'merged-' + team_domain + '-' + channel_name + '.json'), 'w', encoding='utf-8') as f:
        merged.to_json(f)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

