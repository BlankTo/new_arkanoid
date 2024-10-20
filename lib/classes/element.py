"""
element.py

Functions:
- __init__(self, id, description, properties)
  Create an Element, with attributes that are not gonna change.

- __eq__(self, other)
  Compare with:
    - self.__class__
    - int (id == other)
    - str (description == other)

Dependencies:
-
"""

class Element:
    
    def __init__(self, id, description, properties):
        
        self._id = id
        self._description = description
        self._properties = properties

    @property
    def id(self) -> int: return self._id

    @property
    def description(self): return self._description

    @property
    def properties(self): return self._properties

    def __repr__(self):
        return self._description
    
    def __eq__(self, other):

        if isinstance(other, self.__class__): return self._id == other.id
        if isinstance(other, int): return self._id == other
        if isinstance(other, str): return self._description == other

        print(f'{type(other)}')
        raise Exception('Element.__eq__ error')

