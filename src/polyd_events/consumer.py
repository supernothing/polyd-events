import logging
import time

import inflection
from .events import Event, RedisEvent

logger = logging.getLogger(__name__)


class EventConsumer(object):
    def __init__(self, streams, group, consumer_name, db, consume_from_end=False):
        """
        An event consumer

        :param streams: List of stream names
        :param group: The name of this consumer group
        :param consumer_name: The name of this consumer
        :param db: A walrus DB object
        """
        self.db = db
        self.cg = self.db.consumer_group(group, streams, consumer_name)
        self.cg.create(mkstream=True)
        self.stop = False

        if consume_from_end:
            self.cg.set_id('$')

    def get_events(self, count=1, block=0):
        resp = self.cg.read(count, block)

        if resp:
            for stream, events in resp:
                stream = stream.decode('utf-8')
                for event_id, event in events:
                    event_id = event_id.decode('utf-8')
                    if b'event' not in event:
                        logger.warning('got malformed event: %s', str(event))
                        continue
                    event = event[b'event'].decode('utf-8')
                    yield Event.deserialize(event, RedisEvent(getattr(self.cg, inflection.underscore(stream)), event_id))

    def iter_events(self, count=10, block=None, sleep=0.1):
        while True:
            if self.stop:
                break

            num_events = 0
            for event in self.get_events(count=count, block=block):
                yield event
                num_events += 1

            if not num_events:
                time.sleep(sleep)
