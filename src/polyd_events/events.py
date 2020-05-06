import sys
import json
import inflection


class Event(object):
    STR_VALUES = ['event', 'block_number']

    def __init__(self, community, event):
        e_json = json.dumps(event)
        self.__dict__ = event['data']
        self.event = event['event']
        self.block_number = event.get('block_number', -1)
        self.txhash = event.get('txhash', '')
        self.json = e_json
        self.community = community

    @classmethod
    def from_event(cls, community, event):
        cls = getattr(sys.modules[__name__], inflection.camelize(event['event']), Event)
        return cls(community, event)

    def __str__(self):
        return ', '.join(f'{k}: {self.__dict__.get(k, "")}' for k in self.STR_VALUES)

    def serialize(self):
        return json.dumps((self.community, self.json))

    def deserialize(self, data):
        return Event.from_event(*json.loads(data))


class Bounty(Event):
    STR_VALUES = Event.STR_VALUES + ['author', 'sha256', 'artifact_type', 'amount', 'filename', 'extended_type', 'guid']

    def __init__(self, community, event):
        super().__init__(community, event)
        # assumes single-artifact bounty
        self.__dict__.update(self.metadata[0])


class Assertion(Event):
    STR_VALUES = Event.STR_VALUES + ['author', 'bid', 'bounty_guid']

    def __init__(self, community, event):
        super().__init__(community, event)
        try:
            if type(self.bid) == list:
                self.bid = int(self.bid[0])
        except AttributeError:
            print('attr error')
            pass


class Vote(Event):
    STR_VALUES = Event.STR_VALUES + ['voter', 'votes', 'bounty_guid']

    def __init__(self, community, event):
        super().__init__(community, event)
        try:
            if type(self.votes) == list:
                self.votes = int(self.votes[0])
        except AttributeError:
            print('attr error')
            pass
