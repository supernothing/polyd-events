from walrus import Database


class EventProducer(object):
    def __init__(self, stream, *args, **kwargs):
        self.db = Database(*args, **kwargs)
        self.stream = self.db.Stream(stream)

    def add_event(self, event):
        self.stream.add({'event': event.serialize()})
