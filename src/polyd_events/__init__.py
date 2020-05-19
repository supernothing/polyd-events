from . import events, producer, consumer
import inflection as _inflection
event_types = [_inflection.underscore(cls.__name__) for cls in events.Event.__subclasses__()]

communities = [
    'nu',
    'omicron',
    'rho',
]
