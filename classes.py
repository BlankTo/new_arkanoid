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
        return False

class Object:
    def __init__(self, object_id, params= False, elements= None):
        self.id = object_id

        if params:
            self.elements = elements

    def randomize(self, element_pool):
        self.elements = random.sample(element_pool, random.randint(1, len(element_pool)))
        return self

    def __repr__(self):
        return f'object_{self.id}'

    def mutate(self, new_id, element_pool):

        elements = deepcopy(self.elements)

        mutate_what = []

        if len(elements) < len(element_pool): mutate_what.append('add_element')
        if len(elements) > 1: mutate_what.append('remove_element')

        match mutate_what:

            case 'add_element':
                remaining_elements = [element for element in element_pool if element.id not in elements]
                elements.append(random.choice(remaining_elements))  # Add an element

            case 'remove_element':
                elements.remove(random.choice(list(elements)))  # Remove an element

        return Object(new_id, params= True, elements= elements)


    def crossover(self, obj2: 'Object'):
        #TODO
        pass


    def get_elements(self): return [element.id for element in self.elements]

class Category:
    def __init__(self, id, params= False, objects= None, triggers= None, effects= None):
        self.id = id
        
        if params:
            self.objects = objects
            self.triggers = triggers
            self.effects = effects
            n_elements = len(self.get_elements())
            self.rule_usage = [[False for _ in range(n_elements)] for _ in range(len(self.triggers))]

    def randomize(self, object_pool, event_pool):
        self.objects = random.sample(object_pool, random.randint(1, len(object_pool)))
        
        all_pairs = list(itertools.combinations(event_pool, 2))
        chosen_pairs = random.sample(all_pairs, random.randint(0, len(all_pairs)))

        triggers = []
        effects = []
        for trigger, effect in chosen_pairs:
            triggers.append(trigger)
            effects.append(effect)
        
        self.triggers = triggers
        self.effects = effects
        n_elements = len(self.get_elements())
        self.rule_usage = [[False for _ in range(n_elements)] for _ in range(len(self.triggers))]

        return self

#    def mutate_old(self, object_pool, event_pool):
#
#        objects, rules = deepcopy(self.objects), deepcopy(self.rules)
#
#        if random.random() > 0.5:
#
#            if len(objects) > 1 and random.random() > 0.5:
#                objects.remove(random.choice(objects))  # Remove an object
#
#            else:
#                objects.append(random.choice(object_pool))  # Add an object
#
#        else:
#            
#            if len(rules) > 1:
#
#                if len(rules) < pow(len(event_pool), 2) and random.random() > 0.5:
#                    ok = False
#                    while not ok:
#                        ok = True
#                        rule = random.choice(event_pool), random.choice(event_pool) # Create a rule
#                        if rule[0].description in rules.keys():
#                            if rules[rule[0].description] == rule[1]:
#                                ok = False
#
#                else:
#                    del rules[random.choice(list(rules.keys()))] # remove a rule
#
#            else:
#                rules[random.choice(event_pool).description] = random.choice(event_pool) # add a rule
#
#        return Category(self.id, params= True, objects= objects, rules= rules)
    
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
                objects.append(random.choice(object_pool))  # Add an object

            case 'create_rule':
                existing_rules = [(t, e) for t, e in zip(triggers, effects)]
                possible_rules = [rule for rule in list(itertools.product(event_pool, event_pool)) if rule not in existing_rules]
                new_rule = random.choice(possible_rules)
                #print('\ncreate_rule')
                #print(len(triggers))
                #print(existing_rules)
                #print(possible_rules)
                #print(f'new_rule: {new_rule}')
                #print('-----------\n')
                triggers.append(new_rule[0])
                effects.append(new_rule[1])

            case 'mutate_rule':
                ok = False
                while not ok:
                    ok = True

                    to_modify = random.randint(0, len(triggers) - 1)
                    existing_rules = [(t, e) for t, e in zip(triggers, effects)]
                    possible_triggers = [trigger for trigger in event_pool if (trigger, effects[to_modify]) not in existing_rules]
                    possible_effects = [effect for effect in event_pool if (triggers[to_modify], effect) not in existing_rules]

                    if possible_triggers and possible_effects:
                        if random.random() > 0.5: triggers[to_modify] = random.choice(possible_triggers)
                        else: effects[to_modify] = random.choice(possible_effects)
                    
                    elif possible_triggers: triggers[to_modify] = random.choice(possible_triggers)

                    elif possible_effects: effects[to_modify] = random.choice(possible_effects)

                    else: ok = False

                    #print('\nmutate_rule')
                    #print(existing_rules)
                    #print(f'rule_to_modify: {existing_rules[to_modify]}')
                    #print(f'event_pool: {event_pool}')
                    #print(f'possible_triggers: {possible_triggers}')
                    #print(f'possible_effects: {possible_effects}')
                    #print(f'modified_rule: {(self.triggers[to_modify], self.effects[to_modify])}')
                    #print('-----------\n')

            case 'remove_obj':
                objects.remove(random.choice(objects))  # Remove an object

            case 'delete_rule':
                to_delete = random.randint(0, len(triggers) - 1)
                triggers.pop(to_delete)
                effects.pop(to_delete)

        return Category(new_id, params= True, objects= objects, triggers= triggers, effects= effects)


    def crossover(self, cat2: 'Category'):
        #TODO
        pass

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        if obj in self.objects:
            print('object removed')
            self.objects.remove(obj)

    def get_elements(self):
        elements = []
        for obj in self.objects:
            elements.extend(obj.get_elements())
        return list(set(elements))
    
    def get_objects(self): return self.objects
    
    def get_rules(self): return self.triggers, self.effects

    def reset_rule_usage(self):
        n_elements = len(self.get_elements())
        self.rule_usage = [[False for _ in range(n_elements)] for _ in range(len(self.triggers))]
        #self.rule_usage = [False for _ in range(len(self.triggers))]

    def predict(self, events):
            
        predicted_events = []
        for event in events:

            if event.subject in self.get_elements():

                if event.event_type.description in self.triggers:

                    for i, (trigger, effect) in enumerate(zip(self.triggers, self.effects)):

                        if event.event_type.description == trigger:

                            predicted_events.append(Predicted_Event(effect, event.subject))

                            elements = self.get_elements()
                            element_idx = -1
                            for e_i, e_id in enumerate(elements):
                                if e_id == event.subject:
                                    element_idx = e_i
                                    break
                            self.rule_usage[i][element_idx] = True # rule is used on element
        
        return predicted_events

    def get_rule_usage(self):
        return self.rule_usage
    
    def check_obj_and_mutate(self, obj_to_mutate_id, new_obj):
        for i, obj in enumerate(self.objects):
            if obj.id == obj_to_mutate_id:
                self.objects[i] = new_obj
                break

class EventType:
    def __init__(self, description):
        self.description = description

    def __repr__(self):
        return self.description
    
    def __eq__(self, other):
        if isinstance(other, EventType):
            return self.description == other.description
        elif isinstance(other, str):
            return self.description == other
        return False

class Recorded_Event:
    def __init__(self, event_type, subject: 'Element'):
        self.event_type = event_type
        self.subject = subject

    def __repr__(self):
        return str(self.event_type)

class Predicted_Event:
    def __init__(self, event_type, subject: 'Object'):
        self.event_type = event_type
        self.subject = subject

    def __repr__(self):
        return str(self.event_type)

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

        if len(categories) > 1: mutate_what.append('delete_cat')
        if len(objects) > 1: mutate_what.append('delete_obj')

        mutate_what = random.choice(mutate_what)

        match mutate_what:

            case 'create_cat':
                categories.append(Category(self.gen_cat_id()).randomize(objects, self.event_pool)) # Create a new Category

            case 'create_obj':
                new_object = Object(self.gen_obj_id()).randomize(self.element_pool) # Create a new Object
                objects.append(new_object)
                add_to = random.sample(categories, random.randint(1, len(categories))) # adding the object to one or more categories, as just creating it would result in a fixed reduction of fitness
                for cat in add_to:
                    cat.add_object(new_object)

            case 'mutate_cat':
                cat_to_mutate = random.choice(categories)
                categories.remove(cat_to_mutate)
                categories.append(cat_to_mutate.mutate(self.gen_cat_id(), self.objects, self.event_pool))

            case 'mutate_obj':
                obj_to_mutate = random.choice(objects)
                objects.remove(obj_to_mutate)
                new_object = obj_to_mutate.mutate(self.gen_obj_id(), self.element_pool)
                objects.append(new_object)
                for cat in categories:
                    cat.check_obj_and_mutate(obj_to_mutate.id, new_object)

            case 'delete_cat':
                categories.pop(random.randint(0, len(categories) - 1))  # Delete a random category

            case 'delete_obj':
                removed = objects.pop(random.randint(0, len(objects) - 1))  # Remove an object
                for cat in categories:
                    cat.remove_object(removed) # and remove the object from categories

        return Individual(self.gen_obj_id, self.gen_cat_id, params= True, element_pool= self.element_pool, event_pool= self.event_pool, objects= objects, categories= categories)

    def crossover(self, spouse: 'Individual'):

        objects, categories = deepcopy(self.objects), deepcopy(self.categories)
        spouse_objects, spouse_categories = deepcopy(spouse.objects), deepcopy(spouse.categories)

        #TODO crossover


    def predict(self, events):

        predictions = []
        for cat in self.categories:

            predicted_events = cat.predict(events)

            predictions.append({
                'category': cat,
                'predicted_events': predicted_events,
            })

        return predictions

    def set_fitness(self, value): self.fitness = value

    def get_fitness(self): return self.fitness

    def print_rules(self):
        for category in self.categories:
            print(f'category {category.id}:\n')
            print(f'composed of:\n')
            for obj in category.objects:
                print(f'{obj}: {[self.element_pool[i].description for i in range(len(self.element_pool)) if self.element_pool[i].id in obj.get_elements()]}\n')
            print(f'all elements in cat (all objects): {[self.element_pool[i].description for i in range(len(self.element_pool)) if self.element_pool[i].id in category.get_elements()]}')
            print(f'n_rules: {len(category.triggers)}')
            print('rules:')
            for trigger, effect in zip(category.triggers, category.effects):
                print(f'{trigger} -> {effect}')
            print('--------------------------------------------------')

    def get_element_pool(self): return self.element_pool

    def reset_rule_usage(self):
        for cat in self.categories: cat.reset_rule_usage()

    def get_fitness_adjustments(self):

        fitness_adjustment = 0
        objects_in_categories = {}
        elements_in_objects = {}

        for object in self.objects:

            elements = object.get_elements()
            
            #fitness_adjustment += len(elements) # penalty for too many elements in an object

            for element in elements:
                if element in elements_in_objects.keys():
                    elements_in_objects[element] += 1
                else:
                    elements_in_objects[element] = 1
            
        for element_repetitions in elements_in_objects.values():

            if element_repetitions > 1:
                fitness_adjustment += pow(element_repetitions - 1, 3) # penalty for same element in different objects

            elif element_repetitions == 0:
                fitness_adjustment += 100000 # penalty for element not present in any object
                pass


        for category in self.categories:
            objects = category.get_objects()
            
            fitness_adjustment += len(objects) # penalty for too many objects in a category

            fitness_adjustment += list(itertools.chain.from_iterable(category.get_rule_usage())).count(False) * 1000 # penalty for each element to with a rule is never applied

            for object in objects:

                if object.id in objects_in_categories.keys():
                    objects_in_categories[object.id] += 1
                else:
                    objects_in_categories[object.id] = 1
            
        for object_repetitions in objects_in_categories.values():

            if object_repetitions > 1:
                fitness_adjustment += pow(object_repetitions - 1, 5) # penalty for objects repeated in many categories

            elif object_repetitions == 0:
                fitness_adjustment += 100000 # penalty for object not present in any category

        fitness_adjustment += pow(len(self.categories), 3) # penalty for too many categories

        return fitness_adjustment