import random

from .Element import Element


class Object:

    def __init__(self, id, elements: list[Element] = None):
        
        self._id = id
        if elements is None: self._elements: list[Element] = []
        else: self._elements = [elem for elem in elements]

    @property
    def id(self) -> int: return self._id

    @property
    def elements(self) -> list[Element]:
        return self._elements

    def __repr__(self):
        return f'Object_{self._id}({self._elements})'
    
    def __eq__(self, other):

        if isinstance(other, self.__class__): return self._id == other.id
        if isinstance(other, int): return self._id == other
        if isinstance(other, list) and all(isinstance(item, Element) for item in other): return self._elements == other

        print(f'{type(other)}')
        raise Exception('Object.__eq__ error')
    
    def initialize(self, element_pool: list[Element], object_pool: list['Object'] = []) -> 'Object':

        self._elements: list[Element] = random.choice([[elem] for elem in element_pool if [elem] not in object_pool])

        return self
    
    def add_element(self, elem) -> None:
        if elem not in self._elements: self._elements.append(elem)
    
    def remove_element(self, elem, elems_to_add: list[Element] = None) -> None:
        if elem in self._elements: self._elements.remove(elem)
        if elems_to_add:
            for elem in elems_to_add: self.add_element(elem)

    def mutate(self, element_pool: list[Element]) -> None:

        lene = len(self._elements)

        mutate_what = []

        if lene < len(element_pool): mutate_what.append('add_elem')
        if lene > 1: mutate_what.append('remove_elem')

        mutate_what = random.choice(mutate_what)

        match mutate_what:

            case 'add_elem':
                self._elements.append(random.choice([elem for elem in element_pool if elem not in self._elements]))  # Add an element

            case 'remove_elem':
                self._elements.pop(random.randint(0, lene - 1))  # Remove an element
    
    def fuse(self, other: 'Object') -> None:

        for elem in other.elements:
            if elem not in self._elements:
                self._elements.append(elem)

    def divide(self, new_id, no= 1) -> 'Object':

        elems_to_keep = []
        elems_to_move = []

        if no == 1: idx = [random.randint(0, len(self._elements))]
        else: idx = random.choice([i for i in range(len(self._elements))])

        for i, elem in enumerate(self._elements):
            if i in idx: elems_to_move.append(elem)
            else: elems_to_keep.append(elem)

        self._elements: list[Element] = elems_to_keep

        return Object(new_id, elems_to_move)

