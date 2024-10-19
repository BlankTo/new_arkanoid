"""
event_type.py

Functions:
- __init__(self, id, description)
  Create an EventType, with attributes that are not gonna change.

- __eq__(self, other)
  Compare with:
    - self.__class__
    - int (id == other)
    - str (description == other)
    - Event (self == other.event_type)

Dependencies:
-
"""

class EventType:
    
    def __init__(self, id, description):

        self._id = id
        self._description = description

    @property
    def id(self) -> int: return self._id

    @property
    def description(self): return self._description

    def __repr__(self):
        return self._description
    
    def __eq__(self, other):
        
        from .event import Event # here to prevent circular imports
        
        if isinstance(other, self.__class__): return self._id == other.id
        if isinstance(other, int): return self._id == other
        if isinstance(other, str): return self._description == other
        if isinstance(other, Event): return self == other.event_type

        print(f'{type(other)}')
        raise Exception('EventType.__eq__ error')

