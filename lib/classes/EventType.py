

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

        from .Event import Event
        
        if isinstance(other, self.__class__): return self._id == other.id
        if isinstance(other, int): return self._id == other
        if isinstance(other, str): return self._description == other
        if isinstance(other, Event): return self == other.event_type

        print(f'{type(other)}')
        raise Exception('EventType.__eq__ error')

