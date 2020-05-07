import json
import logging
import sys

import inflection


logger = logging.getLogger(__name__)


class Event(object):
    STR_VALUES = ['event', 'block_number']

    def __init__(self, community, event, stream=None):
        e_json = json.dumps(event)
        self.__dict__ = event['data'] if 'data' in event else self.__dict__
        self.event = event['event']
        self.block_number = event.get('block_number', -1)
        self.txhash = event.get('txhash', '')
        self.json = e_json
        self.community = community
        self.stream = stream

    @classmethod
    def from_event(cls, community, event, stream=None):
        cls = getattr(sys.modules[__name__], inflection.camelize(event['event']), Event)
        return cls(community, event, stream)

    def __str__(self):
        return ', '.join(f'{k}: {self.__dict__.get(k, "")}' for k in self.STR_VALUES)

    def serialize(self):
        return json.dumps((self.community, self.json))

    @classmethod
    def deserialize(cls, data, stream=None):
        community, data = json.loads(data)
        data = json.loads(data)
        return Event.from_event(community, data, stream=stream)

    def ack(self):
        if self.stream:
            self.stream.ack()


class Bounty(Event):
    STR_VALUES = Event.STR_VALUES + ['author', 'sha256', 'artifact_type', 'amount', 'filename', 'extended_type', 'guid']

    def __init__(self, community, event, stream=None):
        super().__init__(community, event, stream)
        # assumes single-artifact bounty
        self.__dict__.update(self.metadata[0])


class Assertion(Event):
    STR_VALUES = Event.STR_VALUES + ['author', 'bid', 'bounty_guid']

    def __init__(self, community, event, stream=None):
        super().__init__(community, event, stream)
        try:
            if type(self.bid) == list:
                self.bid = int(self.bid[0])
        except AttributeError:
            pass


class Vote(Event):
    STR_VALUES = Event.STR_VALUES + ['voter', 'votes', 'bounty_guid']

    def __init__(self, community, event, stream=None):
        super().__init__(community, event, stream)
        try:
            if type(self.votes) == list:
                self.votes = int(self.votes[0])
        except AttributeError:
            pass

## Non-PSD events
# TODO do these in a more reasonable way
# just reusing these Event classes for expediency


class FileDownloaded(Event):
    STR_VALUES = ['community', 'path']

    def __init__(self, community, path, bounty, stream=None):
        super().__init__(community, {'event': 'filedownloaded',
                                     'data': {'path': path, 'bounty': json.loads(bounty.json)}}, stream=stream)

    def serialize(self):
        return json.dumps((self.community, self.json))

    @classmethod
    def deserialize(cls, data, stream=None):
        community, data = json.loads(data)
        data = json.loads(data)
        return Event.from_event(community, data, stream=stream)


class RedisEvent(object):
    def __init__(self, stream, event_id):
        self.stream = stream
        self.event_id = event_id

    def ack(self):
        self.stream.ack(self.event_id)
