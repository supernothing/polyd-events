
class EventProducer(object):
    def __init__(self, stream, db):
        """
        An event producer

        :param stream: Stream name
        :param db: Walrus db object
        """
        self.db = db
        self.stream = self.db.Stream(stream)

    def add_event(self, event):
        self.stream.add({'event': event.serialize()})
