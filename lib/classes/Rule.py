import random
import itertools

from .EventType import EventType


class Rule:

    def __init__(self, id, trigger: EventType = None, effect: EventType = None):

        self._id = id
        self._trigger = trigger
        self._effect = effect

    @property
    def id(self):
        return self._id

    @property
    def trigger(self) -> EventType:
        return self._trigger

    @property
    def effect(self) -> EventType:
        return self._effect

    def __repr__(self):
        return f'Rule_{self._id}({self._trigger} -> {self._effect})'

    def __eq__(self, other):

        if isinstance(other, self.__class__): return (self._id == other.id) or ((self._trigger == other.trigger) and (self._effect == other.effect))
        if isinstance(other, int): return self._id == other
        if isinstance(other, tuple): return (self._trigger == other[0]) and (self._effect == other[1])
        if isinstance(other, EventType): return self._trigger == other

        print(f'{type(other)}')
        raise Exception('Rule.__eq__ error')

    def initialize(self, event_pool: list[EventType], rule_pool: list['Rule'] = []) -> 'Rule':

        self._trigger, self._effect = random.choice([(t, e) for t, e in itertools.product(event_pool, event_pool) if (t, e) not in rule_pool])
        
        return self