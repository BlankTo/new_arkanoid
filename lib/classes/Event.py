from .element import Element
from .event_type import EventType

"""
event.py

Functions:
- __init__(self, event_type: EventType, subject: Element)
  Create an Event, with attributes that are not gonna change.

- __eq__(self, other)
  Compare with:
    - self.__class__
    - EventType (trigger == other)
    - tuple (trigger == other[0] and subject == other[1])
    - Element (subject == other)

Dependencies:
-
"""

class Event:

    def __init__(self, event_type: EventType, subject: Element):
        
        self._event_type = event_type
        self._subject = subject

    @property
    def event_type(self) -> EventType: return self._event_type

    @property
    def subject(self): return self._subject

    def __repr__(self):
        return str(self._event_type) + ' on ' + str(self._subject)
    
    def __eq__(self, other):

        if isinstance(other, self.__class__): return (self._event_type == other.event_type) and (self._subject == other.subject)
        if isinstance(other, EventType): return self._event_type == other.event_type
        if isinstance(other, tuple): return self._event_type == other[0] and self._subject == other[1]
        if isinstance(other, Element): return self._subject == other
        
        print(f'{type(other)}')
        raise Exception('Event.__eq__ error')
    
    