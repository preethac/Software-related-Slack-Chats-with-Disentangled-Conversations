#!/usr/bin/env python3

from datetime import datetime, timedelta
import argparse
import configparser
import os.path
import sys
import time

import requests
from slacker import Slacker

from muse.block import Block
from muse.datasource import DataSource
from muse.paths import mkdir_p
from muse.times import get_unix_epoch_timestamp


class SlackException(Exception):
    pass


class SlackChannelNotFoundException(SlackException):
    pass


class SlackDataSource(DataSource):
    def __init__(self, token: str, channel_name: str, root_directory=None):
        super().__init__(root_directory)
        self._client = Slacker(token)
        self.channel_name = channel_name
        self._domain = None

    @property
    def directory(self):
        return os.path.join(self.root_directory, 'slack', self.team_domain, self.channel_name)

    @property
    def team_domain(self):
        if self._domain is None:
            team_query = self._client.team.info()
            if not team_query.successful:
                raise SlackException(team_query.error)
            self._domain = team_query.body['team']['domain']
        return self._domain

    def _get_id_for_channel(self, channel_name: str):
        return self._client.channels.get_channel_id(channel_name)

    def fetch(self, start=datetime.fromtimestamp(get_unix_epoch_timestamp()), end=datetime.now(), page_size=100):
        channel_id = self._get_id_for_channel(self.channel_name)
        if channel_id is None:
            raise SlackChannelNotFoundException(
                '{0} channel does not exist'.format(self.channel_name))

        if start.timestamp() == float(get_unix_epoch_timestamp()):
            start = 0
        else:
            start = start.timestamp()

        response = self._client.channels.history(channel_id, latest=end.timestamp(), oldest=start,
                                                 count=page_size, inclusive=True)

        while response.successful:
            for message in response.body['messages']:
                yield message

            if not response.body['has_more']:
                break

            latest = response.body['messages'][-1]['ts']
            try:
                response = self._client.channels.history(channel_id, latest=latest, oldest=start,
                                                         count=page_size, inclusive=False)
            except requests.exceptions.HTTPError as ex:
                if ex.response.status_code == 429:
                    time.sleep(int(ex.response.headers['Retry-After']))
                    response = self._client.channels.history(channel_id, latest=latest, oldest=start,
                                                             count=page_size, inclusive=False)
                else:
                    raise

    def format_file_name(self, end_date: datetime, days):
        filename = '{0:04d}{1:02d}{2:02d}_{3:03d}'.format(
            end_date.year, end_date.month, end_date.day, days)
        return os.path.join(self.directory, filename)

    def update(self, end_date=datetime.now(), page_size=100, weeks=0, days=30, hours=0):
        delta = timedelta(days=days, hours=hours, weeks=weeks)
        start_date = end_date - delta

        children = [self.make_block_from_message(m)
                    for m in self.fetch(start_date, end_date, page_size)]
        block = Block({
            'team_domain': self.team_domain,
            'channel_name': self.channel_name,
            'start_date': start_date,
            'end_date': end_date
        }, children)

        mkdir_p(self.directory)
        file_path = self.format_file_name(end_date, delta.days) + '.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            block.to_json(f)

    def __str__(self):
        return '{0} #{1}'.format(self.team_domain, self.channel_name)

    @staticmethod
    def make_block_from_message(message):
        return Block(message)


def read_config(file_name='slack.ini', root_directory=None):
    """
    reads the given file name and returns a generator of slack data sources
    """
    parser = configparser.ConfigParser()
    parser.read(file_name)
    for community in parser.sections():
        token = parser[community]['token']
        channels = [c.strip()
                    for c in parser[community]['channels'].split(',')]
        for channel in channels:
            yield SlackDataSource(token, channel, root_directory=root_directory)
