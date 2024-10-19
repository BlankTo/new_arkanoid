import random
import itertools
from copy import deepcopy

class ID_creator:
    def __init__(self):
        self.id = -1
    def get_id(self):
        self.id += 1
        return self.id


class Element:
    def __init__(self, element_id, description, attributes):

        self.id = element_id
        self.description = description
        self.attributes = attributes  # Dictionary of element properties

    def __repr__(self):
        return self.description
    
    def __eq__(self, other):
        if isinstance(other, Element):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        elif isinstance(other, str):
            return self.description == other
        
        raise Exception('Element.__eq__ error')


class Object:

    def __init__(self, id, params= False, elements= None):

        self.id = id

        if params:
            self.elements = elements

    def randomize(self, element_pool):

        #self.elements = random.sample(element_pool, random.randint(1, len(element_pool))) # starting with one or more elements inside
        self.elements = [random.choice(element_pool)] # starting with one elements inside

        return self

    def __repr__(self):
        return f'object_{self.id}'
    
    def __eq__(self, other):
        if isinstance(other, Object):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        
        raise Exception('Object.__eq__ error')

    def mutate(self, new_id, element_pool):

        elements = deepcopy(self.elements)

        mutate_what = []

        if len(elements) < len(element_pool): mutate_what.append('add_elem')
        if len(elements) > 1: mutate_what.append('remove_elem')

        mutate_what = random.choice(mutate_what)

        match mutate_what:

            case 'add_elem':
                #print('add_elem')
                elements.append(random.choice([elem for elem in element_pool if elem not in elements]))  # Add an element

            case 'remove_elem':
                #print('remove_elem')
                elements.remove(random.choice(list(elements)))  # Remove an element

        return Object(new_id, params= True, elements= elements)
    
    def fuse(self, obj2: 'Object', new_id):

        elements = deepcopy(self.elements)
        for elem in obj2.elements:
            if elem not in elements:
                elements.append(elem)

        return Object(new_id, params= True, elements= elements)
    
    def crossover(self, obj2: 'Object'):
        #TODO
        pass

    def get_elements(self):
        return self.elements

    def get_elements_id(self):
        return [elem.id for elem in self.elements]
    
    def remove_element(self, new_id, elem_id):

        elements = [elem for elem in deepcopy(self.elements) if elem.id != elem_id]

        return Object(new_id, params= True, elements= elements)

    def add_element(self, new_id, new_elem):

        elements = deepcopy(self.elements)
        elements.append(new_elem)
        
        return Object(new_id, params= True, elements= elements)
    
    def contains(self, elem_id):
        return elem_id in self.elements


class EventType:
    def __init__(self, id, description):
        self.id = id
        self.description = description

    def __repr__(self):
        return self.description
    
    def __eq__(self, other):
        if isinstance(other, EventType):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        elif isinstance(other, str):
            return self.description == other
        
        raise Exception('EventType.__eq__ error')


class Event:
    def __init__(self, event_type, subject: 'Element'):
        self.event_type = event_type
        self.subject = subject

    def __repr__(self):
        return str(self.event_type) + ' on ' + str(self.subject)
    
    def __eq__(self, other):
        if isinstance(other, Event):
            return (self.event_type == other.event_type) and (self.subject == other.subject)
        elif isinstance(other, EventType):
            return self.event_type == other

        raise Exception('Event.__eq__ error')


class Category:
    def __init__(self, id, params= False, objects= None, triggers= None, effects= None):

        self.id = id
        
        if params:
            self.objects = objects
            self.triggers = triggers
            self.effects = effects
            self.rule_usage = [[-1 for _ in range(len(self.get_elements_id()))] for _ in range(len(self.triggers))]

    def __repr__(self):
        return f'cat_{self.id}'

    def randomize(self, object_pool, event_pool):
        
        #self.objects = random.sample(object_pool, random.randint(1, len(object_pool)))
        self.objects = [random.choice(object_pool)]
        
        all_pairs = list(itertools.combinations(event_pool, 2))
        chosen_pairs = random.sample(all_pairs, random.randint(0, len(all_pairs)))

        triggers = []
        effects = []
        for t, e in chosen_pairs:
            triggers.append(t)
            effects.append(e)
        
        self.triggers = triggers
        self.effects = effects
        self.rule_usage = [[-1 for _ in range(len(self.get_elements_id()))] for _ in range(len(self.triggers))]

        return self
    
    def mutate(self, new_id, object_pool, event_pool):

        objects, triggers, effects = deepcopy(self.objects), deepcopy(self.triggers), deepcopy(self.effects)

        mutate_what = []

        if len(objects) < len(object_pool): mutate_what.append('add_obj')
        if len(objects) > 1: mutate_what.append('remove_obj')
        if len(triggers) < pow(len(event_pool), 2): mutate_what.append('create_rule')
        if len(triggers) > 0:
            mutate_what.append('mutate_rule')
            mutate_what.append('delete_rule')

        mutate_what = random.choice(mutate_what)

        match mutate_what:

            case 'add_obj':
                #print('add_obj')
                objects.append(random.choice(object_pool))  # Add an object

            case 'create_rule':
                #print('\ncreate_rule')
                #if not triggers: print('no rules yet')
                #for t, e in zip(triggers, effects):
                #    print(f'{t} -> {e}')
                existing_rules = [(t, e) for t, e in zip(triggers, effects)]
                possible_rules = [r for r in list(itertools.product(event_pool, event_pool)) if r not in existing_rules]
                new_rule = random.choice(possible_rules)
                triggers.append(new_rule[0])
                effects.append(new_rule[1])
                #print('------')
                #for t, e in zip(triggers, effects):
                #    print(f'{t} -> {e}')
                #input('...')

            case 'mutate_rule':
                #print('\nmutate_rule')
                #if not triggers: print('no rules yet')
                #for t, e in zip(triggers, effects):
                #    print(f'{t} -> {e}')
                ok = False
                while not ok:
                    ok = True

                    to_modify = random.randint(0, len(triggers) - 1)
                    existing_rules = [(t, e) for t, e in zip(triggers, effects)]
                    possible_triggers = [t for t in event_pool if (t, effects[to_modify]) not in existing_rules]
                    possible_effects = [e for e in event_pool if (triggers[to_modify], e) not in existing_rules]

                    if possible_triggers and possible_effects:
                        if random.random() > 0.5: triggers[to_modify] = random.choice(possible_triggers)
                        else: effects[to_modify] = random.choice(possible_effects)
                    
                    elif possible_triggers: triggers[to_modify] = random.choice(possible_triggers)

                    elif possible_effects: effects[to_modify] = random.choice(possible_effects)

                    else: ok = False

                #print('------')
                #for t, e in zip(triggers, effects):
                #    print(f'{t} -> {e}')
                #input('...')

            case 'remove_obj':
                #print('remove_obj')
                objects.remove(random.choice(objects))  # Remove an object

            case 'delete_rule':
                #print('\ndelete_rule')
                #if not triggers: print('no rules yet')
                #for t, e in zip(triggers, effects):
                #    print(f'{t} -> {e}')
                to_delete = random.randint(0, len(triggers) - 1)
                triggers.pop(to_delete)
                effects.pop(to_delete)
                #print('------')
                #for t, e in zip(triggers, effects):
                #    print(f'{t} -> {e}')
                #input('...')

        return Category(new_id, params= True, objects= objects, triggers= triggers, effects= effects)
    

    def fuse(self, cat2: 'Category', new_id):
        objects = deepcopy(self.objects)
        for obj in cat2.objects:
            if obj not in objects:
                objects.append(obj)
                
        triggers = deepcopy(self.triggers)
        effects = deepcopy(self.effects)
        rules = [(t, e) for t, e in zip(triggers, effects)]
        for t, e in zip(cat2.triggers, cat2.effects):
            if (t, e) not in rules:
                triggers.append(t)
                effects.append(e)

        return Category(new_id, params= True, objects= objects, triggers= triggers, effects= effects)


    def crossover(self, cat2: 'Category'):
        #TODO
        pass

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj_id, new_object= None):
        if isinstance(obj_id, int):
            obj_id = [obj_id]
        if new_object is None:
            self.objects = [obj for obj in self.objects if obj.id not in obj_id]
            return
        
        objects = []
        found = False
        for obj in self.objects:
            if obj.id in obj_id:
                found = True
            else:
                objects.append(obj)
        if found:
            objects.append(new_object)
        self.objects = objects

    def get_elements(self):
        elements = []
        for obj in self.objects:
            for elem in obj.get_elements():
                if elem not in elements:
                    elements.append(elem)
        return elements

    def get_elements_id(self):
        elements_id = []
        for obj in self.objects:
            elements_id.extend(obj.get_elements_id())
        return list(set(elements_id))
    
    def get_objects(self):
        return self.objects
    
    def contains(self, obj_id):
        return obj_id in self.objects
    
    def get_rules(self):
        return self.triggers, self.effects

    def reset_rule_usage(self):
        self.rule_usage = [[-1 for _ in range(len(self.get_elements_id()))] for _ in range(len(self.triggers))]

    def predict(self, events):

        elements_id = self.get_elements_id()
            
        predicted_events = []
        for event in events:

            if event.subject in elements_id:

                if event.event_type in self.triggers: # .event_type is not necessary

                    for i, (trigger, effect) in enumerate(zip(self.triggers, self.effects)):

                        if event.event_type == trigger: # .event_type is not necessary

                            element_idx = None
                            for elem_i, elem_id in enumerate(elements_id):
                                if elem_id == event.subject:
                                    element_idx = elem_i
                                    break

                            predicted_events.append(Event(effect, event.subject))

                            self.rule_usage[i][element_idx] = 0 # rule is used on element

        return predicted_events

    def predict_and_check(self, events, next_frame_events):

        elements_id = self.get_elements_id()
            
        for event in events:

            if event.subject in elements_id:

                if event.event_type in self.triggers:

                    for i, (trigger, effect) in enumerate(zip(self.triggers, self.effects)):

                        if event.event_type == trigger:
                            element_idx = None
                            for elem_i, elem_id in enumerate(elements_id):
                                if elem_id == event.subject:
                                    element_idx = elem_i
                                    break

                            self.rule_usage[i][element_idx] = 0 # rule is used on element

                            # check against next_frame_events

                            correct = False

                            for nfe in next_frame_events:

                                if effect == nfe.event_type and event.subject == nfe.subject:
                                    correct = True
                                    break

                            if correct:
                                #print(f'correct: {[(e.event_type, e.subject) for e in events]} -> {(predicted_event.event_type, predicted_event.subject)}')
                                if self.rule_usage[i][element_idx] != 2: # not wrong
                                    self.rule_usage[i][element_idx] = 1
                            else:
                                #print(f'wrong: {[(e.event_type, e.subject) for e in events]} -> {(predicted_event.event_type, predicted_event.subject)}')
                                self.rule_usage[i][element_idx] = 2

    def get_rule_usage(self):
        return self.rule_usage
    
    def init_rules(self, objects, event_pool):

        self.objects = objects
        
        all_pairs = list(itertools.combinations(event_pool, 2))

        #chosen_pairs = random.sample(all_pairs, random.randint(0, len(all_pairs))) # more than one
        chosen_pairs = [random.choice(all_pairs)] # only one

        triggers = []
        effects = []
        for t, e in chosen_pairs:
            triggers.append(t)
            effects.append(e)
        
        self.triggers = triggers
        self.effects = effects
        self.rule_usage = [[-1 for _ in range(len(self.get_elements_id()))] for _ in range(len(self.triggers))]

        return self
        

class Individual:
    def __init__(self, gen_obj_id, gen_cat_id, params= False, element_pool= None, event_pool= None, objects= None, categories= None):
        
        self.gen_obj_id = gen_obj_id
        self.gen_cat_id = gen_cat_id
        
        if params:
            self.element_pool = element_pool
            self.event_pool = event_pool
            self.objects = objects
            self.categories = categories
            self.fitness = 0

    def randomize(self, element_pool, event_pool, min_starting_objects= 5, max_starting_objects= 10, min_starting_categories= 5, max_starting_categories= 10):
        self.element_pool = element_pool
        self.event_pool = event_pool

        objects = []
        categories = []

        num_objects = random.randint(min_starting_objects, max_starting_objects)
        for _ in range(num_objects):
            objects.append(Object(self.gen_obj_id()).randomize(self.element_pool))

        num_categories = random.randint(min_starting_categories, max_starting_categories)
        for _ in range(num_categories):
            categories.append(Category(self.gen_cat_id()).randomize(objects, self.event_pool))

        self.objects = objects
        self.categories = categories
        self.fitness = 0

        return self


    def mutate(self):

        objects, categories = deepcopy(self.objects), deepcopy(self.categories)

        mutate_what = ['create_cat', 'create_obj', 'mutate_cat', 'mutate_obj']

        #if len(categories) > 0:
        #    mutate_what.append('divide_cat') #TODO magari non tenere regole cat di partenza e crearne una nuova di partenza
        #if len(objects) > 0:
        #    mutate_what.append('divide_obj') #TODO magari no, rischia di essere peggiorativa
        if len(categories) > 1:
            ok_cats = []
            for cat in categories:
                if len(cat.get_objects()) > 1:
                    ok_cats.append(cat)
            if ok_cats:
                mutate_what.append('move_obj')
                mutate_what.append('divide_cat')
                    #break
            mutate_what.append('fuse_cat')
            mutate_what.append('delete_cat')
        if len(objects) > 1:
            ok_objs = []
            for obj in objects:
                if len(obj.get_elements_id()) > 1:
                    ok_objs.append(obj)
            if ok_objs:
                mutate_what.append('move_elem')
            mutate_what.append('fuse_obj')
            mutate_what.append('delete_obj')

        mutate_what = random.choice(mutate_what)

        #print('\n-----------------------------------------------------------')
        #print(objects)
        #for cat in categories:
        #    print(f'{cat} -> {[f"{o}({o.elements})" for o in cat.objects]}')

        match mutate_what:

            case 'create_cat':
                #print('create_cat')
                categories.append(Category(self.gen_cat_id()).randomize(objects, self.event_pool)) # Create a new Category

            case 'create_obj':
                #print('create_obj')
                new_object = Object(self.gen_obj_id()).randomize(self.element_pool) # Create a new Object
                objects.append(new_object)

                #add to one or more cat
                #add_to = random.sample(categories, random.randint(1, len(categories))) # adding the object to one or more categories, as just creating it would result in a fixed reduction of fitness
                #for cat in add_to:
                #    cat.add_object(new_object)

                #add to only one cat
                random.choice(categories).add_object(new_object) # adding the object to one or more categories, as just creating it would result in a fixed reduction of fitness

            case 'mutate_cat':
                #print('mutate_cat')
                cat_to_mutate = random.choice(categories)
                categories.remove(cat_to_mutate)
                categories.append(cat_to_mutate.mutate(self.gen_cat_id(), self.objects, self.event_pool)) # mutate the chosen category

            case 'mutate_obj':
                #print('mutate_obj')
                obj_to_mutate = random.choice(objects)
                objects.remove(obj_to_mutate)
                new_object = obj_to_mutate.mutate(self.gen_obj_id(), self.element_pool) # mutate the chosen object
                objects.append(new_object)
                for cat in categories: # and update categories
                    cat.remove_object(obj_to_mutate.id, new_object)

            case 'move_obj': # CHECK HERE
                #print('move_obj')
                from_cat = random.choice(ok_cats)
                obj_to_move = random.choice(from_cat.get_objects())
                ok_cats = []
                for cat in categories:
                    if not cat.contains(obj_to_move.id):
                        ok_cats.append(cat)
                if ok_cats:
                    to_cat = random.choice(ok_cats)
                    #print(f'from_cat: {from_cat}')
                    #print(f'to_cat: {to_cat}')
                    #print(f'to_move: {obj_to_move}')
                    from_cat.remove_object(obj_to_move.id)
                    to_cat.add_object(obj_to_move)

            case 'move_elem': # CHECK HERE
                #print('move_elem')
                from_obj = random.choice(ok_objs)
                elem_to_move = random.choice(from_obj.get_elements())
                ok_objs = []
                for obj in objects:
                    if not obj.contains(elem_to_move.id):
                        ok_objs.append(obj)
                if ok_objs:
                    to_obj = random.choice(ok_objs)
                    #print(f'from_obj: {from_obj}')
                    #print(f'to_obj: {to_obj}')
                    #print(f'to_move: {elem_to_move}')
                    new_obj_0 = from_obj.remove_element(self.gen_obj_id(), elem_to_move.id)
                    new_obj_1 = to_obj.add_element(self.gen_obj_id(), elem_to_move)
                
                    objects.remove(from_obj)
                    objects.remove(to_obj)
                    objects.append(new_obj_0)
                    objects.append(new_obj_1)

                    for cat in categories: # and update categories
                        cat.remove_object(from_obj.id, new_obj_0)
                        cat.remove_object(to_obj.id, new_obj_1)

            case 'fuse_cat':
                #print('fuse_cat')
                cats_to_mutate = random.sample(categories, 2)
                categories.remove(cats_to_mutate[0])
                categories.remove(cats_to_mutate[1])
                categories.append(cats_to_mutate[0].fuse(cats_to_mutate[1], self.gen_cat_id()))

            case 'fuse_obj':
                #print('fuse_obj')
                objs_to_mutate = random.sample(objects, 2)
                objects.remove(objs_to_mutate[0])
                objects.remove(objs_to_mutate[1])
                new_object = objs_to_mutate[0].fuse(objs_to_mutate[1], self.gen_obj_id()) # fuse two objects in one
                objects.append(new_object)
                for cat in categories: # and update categories
                    cat.remove_object([objs_to_mutate[0].id, objs_to_mutate[1].id], new_object)

            case 'divide_cat': # CHECK HERE
                #print('divide_cat')
                from_cat = random.choice(ok_cats)
                obj_to_move = random.choice(from_cat.get_objects())
                #print(f'from_cat: {from_cat}')
                #print(f'to_move: {obj_to_move}')
                from_cat.remove_object(obj_to_move.id)
                categories.append(Category(self.gen_cat_id()).init_rules([obj_to_move], self.event_pool))

            case 'delete_cat':
                #print('delete_cat')
                categories.pop(random.randint(0, len(categories) - 1))  # Delete a random category

            case 'delete_obj':
                #print('delete_obj')
                removed = objects.pop(random.randint(0, len(objects) - 1))  # Remove an object
                for cat in categories:
                    cat.remove_object(removed.id) # and remove the object from categories

        #print(objects)
        #for cat in categories:
        #    print(f'{cat} -> {[f"{o}({o.elements})" for o in cat.objects]}')
        #print()
        #input('...')

        return Individual(self.gen_obj_id, self.gen_cat_id, params= True, element_pool= self.element_pool, event_pool= self.event_pool, objects= objects, categories= categories)

    def crossover(self, spouse: 'Individual'):

        objects, categories = deepcopy(self.objects), deepcopy(self.categories)
        spouse_objects, spouse_categories = deepcopy(spouse.objects), deepcopy(spouse.categories)

        #TODO crossover


    def predict(self, events):

        predictions = []
        for cat in self.categories:
            predictions.extend(cat.predict(events))

        return predictions


    def predict_and_check(self, events, next_frame_events):

        for cat in self.categories:
            cat.predict_and_check(events, next_frame_events)

    def set_fitness(self, value): self.fitness = value

    def get_fitness(self): return self.fitness

    def print_rules(self):
        print('\ncategories:\n')
        for cat in self.categories:
            print('----')
            print(f'category {cat.id}:')
            print(f'composed of:\n')
            for obj in cat.objects:
                print(f'{obj}: {[self.element_pool[i] for i in range(len(self.element_pool)) if self.element_pool[i].id in obj.get_elements_id()]}')
            print('rules:')
            for trigger, effect in zip(cat.triggers, cat.effects):
                print(f'{trigger} -> {effect}')

    def get_element_pool(self):
        return self.element_pool

    def reset_rule_usage(self):
        for cat in self.categories:
            cat.reset_rule_usage()

    def get_categories(self):
        return self.categories

    def get_fitness_adjustments(self):

        fitness_adjustment = 0
        objects_in_categories = {obj.id: 0 for obj in self.objects}
        elements_in_objects = {elem.id: 0 for elem in self.get_element_pool()}

        for object in self.objects:

            elements_id = object.get_elements_id()
            
            fitness_adjustment += len(elements_id) # penalty for too many elements in an object

            for elem_id in elements_id:
                elements_in_objects[elem_id] += 1

        #print(elements_in_objects)
            
        for element_repetitions in elements_in_objects.values():

            if element_repetitions > 1:
                fitness_adjustment += pow(1000, element_repetitions - 1) # penalty for same element in different objects
                pass

            elif element_repetitions == 0:
                fitness_adjustment += 100000000 # penalty for element not present in any object
                pass


        for cat in self.categories:
            objects = cat.get_objects()
            
            fitness_adjustment += len(objects) # penalty for too many objects in a category

            for obj in objects:
                if obj.id in objects_in_categories.keys():
                    objects_in_categories[obj.id] += 1
                else:
                    raise Exception(f'misaligned objects error - get_fitness_adjustments\nobjects:{self.objects}\nobj: {obj}')
        
        #print(objects_in_categories)

        for object_repetitions in objects_in_categories.values():

            if object_repetitions > 1:
                fitness_adjustment += pow(1000, object_repetitions - 1) # penalty for objects repeated in many categories
                pass

            elif object_repetitions == 0:
                fitness_adjustment += 100000 # penalty for object not present in any category

        fitness_adjustment += len(self.categories) # penalty for too many categories

        return fitness_adjustment