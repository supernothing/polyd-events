import json

from walrus import Database
from .events import Event, RedisEvent


class EventConsumer(object):
    def __init__(self, streams, consumer_name, *args, **kwargs):
        self.db = Database(*args, **kwargs)
        self.cg = self.db.consumer_group(consumer_name, streams)
        self.cg.create(mkstream=True)
        self.stop = False

    def get_events(self, count=1, block=0):
        resp = self.cg.read(count, block)

        if resp:
            for stream, events in resp:
                stream = stream.decode('utf-8')
                for event_id, event in events:
                    print(stream, event_id, event)
                    event_id = event_id.decode('utf-8')
                    event = event[b'event'].decode('utf-8')
                    yield Event.deserialize(event, RedisEvent(getattr(self.cg, stream), event_id))

    def iter_events(self):
        while True:
            if self.stop:
                break

            for event in self.get_events(block=1):
                yield event
