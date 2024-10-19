import random
import itertools

from .Element import Element
from .Object import Object
from .Event import Event
from .Rule import Rule


class Category:

    def __init__(self, id, objects: list[Object] = None, rules: list[Rule] = None):

        self._id = id

        if objects is None or rules is None:
            self._objects = []
            self._rules = []
        
        else:
            self._objects = [obj for obj in objects]
            self._rules = [rule for rule in rules]

    @property
    def id(self):
        return self._id

    @property
    def objects(self) -> list[Object]:
        return self._objects

    @property
    def rules(self) -> list[Rule]:
        return self._rules

    def __repr__(self):
        out = f'Category_{self.id}:\n\nObjects:\n'
        if not self._objects: out += 'No Objects\n'
        for obj in self._objects:
            out += f'{obj}\n'
        out += '\nRules:\n'
        if not self._rules: out += 'No Rules\n'
        for rule in self._rules:
            out += f'{rule}\n'
        out += '\n'
        return out

    def __eq__(self, other):

        if isinstance(other, self.__class__): return self._id == other.id
        if isinstance(other, int): return self._id == other
        if isinstance(other, tuple): return (self._objects == other[0]) and (self._rules == other[1])

        print(f'{type(other)}')
        raise Exception('Category.__eq__ error')

    def initialize(self, object_pool: list[Object], rule_pool: list[Event], category_pool: list['Category'] = []) -> 'Category':

        if rule_pool:
            self._objects, self._rules = random.choice([([o], [r]) for o, r in itertools.product(object_pool, rule_pool) if ([o], [r]) not in category_pool])
        else:
            self._objects, self._rules = random.choice([([o], []) for o in object_pool if ([o], []) not in category_pool])
        return self
    
    def add_object(self, obj) -> None:
        if obj not in self._objects: self._objects.append(obj)

    def add_rule(self, rule) -> None:
        if rule not in self._rules: self._rules.append(rule)
    
    def remove_object(self, obj, objs_to_add: list[Object] = None) -> None:
        if obj in self._objects: self._objects.remove(obj)
        if objs_to_add:
            for obj in objs_to_add: self.add_object(obj)

    def remove_rule(self, rule) -> None:
        if rule in self._rules: self._rules.remove(rule)

    def mutate(self, object_pool: list[Element], rule_pool: list[Event]) -> None:

        leno = len(self._objects)
        lenr = len(self._rules)

        mutate_what = []

        if leno < len(object_pool): mutate_what.append('add_obj')
        if leno > 1: mutate_what.append('remove_obj')
        if lenr < len(rule_pool): mutate_what.append('add_rule')
        if lenr > 0: mutate_what.append('remove_rule')

        if mutate_what: mutate_what = random.choice(mutate_what)
        else: return

        match mutate_what:

            case 'add_obj':
                self._objects.append(random.choice([obj for obj in object_pool if obj not in self._objects]))  # Add an Object

            case 'remove_obj':
                self._objects.pop(random.randint(0, leno - 1))  # Remove an Object

            case 'add_rule':
                self._rules.append(random.choice([rule for rule in rule_pool if rule not in self._rules]))  # Add a Rule

            case 'remove_rule':
                self._rules.pop(random.randint(0, lenr - 1))  # Remove a Rule

    def fuse(self, other: 'Category') -> None:

        for obj in other.objects:
            if obj not in self._objects:
                self._objects.append(obj)

        for rule in other.rules:
            if rule not in self._rules:
                self._rules.append(rule)

    def divide_new_rule(self, new_id, rule_pool, no= 1) -> 'Category':

        objs_to_keep = []
        objs_to_move = []

        if no == 1: idx = [random.randint(0, len(self._objects))]
        else: idx = random.choice([i for i in range(len(self._objects))])

        for i, obj in enumerate(self._objects):
            if i in idx: objs_to_move.append(obj)
            else: objs_to_keep.append(obj)

        self._objects = objs_to_keep

        return Category(new_id, objs_to_move, Category.init_rand(rule_pool))
    

    ## for old fitness

    def get_elements_id(self):
        elements_id = []
        for obj in self._objects:
            for elem in obj.elements:
                elements_id.append(elem.id)
        return list(set(elements_id))