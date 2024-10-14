import random
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

    def mutate(self, element_pool):

        elements = deepcopy(self.elements)

        if len(elements) > 1:

            if len(elements) < len(element_pool) and random.random() > 0.5:
                remaining_elements = [element for element in element_pool if element.id not in elements]
                elements.append(random.choice(remaining_elements))  # Add an element

            else:
                elements.remove(random.choice(list(elements)))  # Remove an element

        else:
            remaining_elements = [element for element in element_pool if element.id not in elements]
            elements.append(random.choice(remaining_elements))  # Add an element

        return Object(self.id, params= True, elements= elements)


    def crossover(self, obj2: 'Object'):
        #TODO
        pass


    def get_elements(self): return [element.id for element in self.elements]

class Category:
    def __init__(self, id, params= False, objects= None, rules= None):
        self.id = id
        
        if params:
            self.objects = objects
            self.rules = rules

    def randomize(self, object_pool, event_pool):
        self.objects = random.sample(object_pool, random.randint(1, len(object_pool)))
        
        triggers = random.sample(event_pool, random.randint(1, len(event_pool)))
        rules = {}
        for trigger in triggers:
            rules[trigger.description] = random.choice(event_pool)
        self.rules = rules

        return self

    def mutate(self, object_pool, event_pool):

        objects, rules = deepcopy(self.objects), deepcopy(self.rules)

        if random.random() > 0.5:

            if len(objects) > 1 and random.random() > 0.5:
                objects.remove(random.choice(objects))  # Remove an object

            else:
                objects.append(random.choice(object_pool))  # Add an object

        else:
            
            if len(rules) > 1:

                if len(rules) < pow(len(event_pool), 2) and random.random() > 0.5:
                    ok = False
                    while not ok:
                        ok = True
                        rule = random.choice(event_pool), random.choice(event_pool)
                        if rule[0].description in rules.keys():
                            if rules[rule[0].description] == rule[1]:
                                ok = False

                else:
                    del rules[random.choice(list(rules.keys()))] # remove a rule

            else:
                rules[random.choice(event_pool).description] = random.choice(event_pool) # add a rule

        return objects, rules

    def crossover(self, cat2: 'Category'):
        #TODO
        pass

    def remove_object(self, obj):
        if obj in self.objects: self.objects.remove(obj)

    def get_elements(self):
        elements = []
        for obj in self.objects:
            elements.extend(obj.get_elements())
        return set(elements)
    
    def get_objects(self): return self.objects
    
    def get_rules(self): return self.rules

    def get_fitness_adjustments(self):

        fitness_adjustment = 0
        elements_in_objects = {}

        for object in self.objects:
            elements = object.get_elements()
            for element in elements:
                if element in elements_in_objects.keys():
                    elements_in_objects[element] += 1
                else:
                    elements_in_objects[element] = 1
            
        for element_repetitions in elements_in_objects.values():

            if element_repetitions > 1:
                fitness_adjustment += pow(element_repetitions - 1, 3)

            elif element_repetitions == 0:
                fitness_adjustment += 10

        return fitness_adjustment

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
    
#class Rule:
#    def __init__(self, rule_id): riscrivere mettendo sia la possibilita di avere regole che non hanno soggetto, che hanno soggetto singolo e che hanno soggetti multipli e oggetti
#        self.rule_id = rule_id
#
#    def __repr__(self):
#        pass
#
#    def randomize(self, event_pool): # , actors_pool
#            pass
#
#    def mutate(self, event_pool): # , actors_pool
#        pass
#
#    def crossover(self, object2: 'Rule'):
#        pass

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

        mutate_what = random.randint(0, 3)

        if mutate_what == 0:
            # Mutate Objects
            random.choice(objects).mutate(self.element_pool)

        if mutate_what == 1:
            # Addition/Removal of objects
            if random.random() > 0.5:
                if len(objects) > 1:
                    if random.random() > 0.5:
                        objects.append(Object(self.gen_obj_id()).randomize(self.element_pool)) # Add a new Object
                        #TODO add object to one or more category, else it will be always a worsening solution
                    else:
                        removed = objects.pop(random.randint(0, len(objects) - 1))  # Remove an object
                        for cat in categories:
                            cat.remove_object(removed)

                else:
                    objects.append(Object(self.gen_obj_id()).randomize(self.element_pool)) # Add a new Object

        if mutate_what == 2:
            # Mutate Categories
            random.choice(categories).mutate(objects, self.event_pool)

        if mutate_what == 3:
            # Addition/Removal of categories
            if random.random() > 0.5:
                if random.random() > 0.5 and len(categories) > 1:
                    categories.pop(random.randint(0, len(categories) - 1))  # Remove a random category
                else:
                    categories.append(Category(self.gen_cat_id()).randomize(objects, self.event_pool)) # Add a new Category

        return Individual(self.gen_obj_id, self.gen_cat_id, params= True, element_pool= self.element_pool, event_pool= self.event_pool, objects= objects, categories= categories)

    def crossover(self, spouse: 'Individual'):

        objects, categories = deepcopy(self.objects), deepcopy(self.categories)
        spouse_objects, spouse_categories = deepcopy(spouse.objects), deepcopy(spouse.categories)

        #TODO crossover


    def predict(self, events):

        predictions = []
        for category in self.categories:

            elements_in_category = category.get_elements()
            
            predicted_events = []
            for event in events:

                if event.subject in elements_in_category:

                    if event.event_type.description in category.rules.keys():
                        predicted_events.append(Predicted_Event(category.rules[event.event_type.description], event.subject))

            predictions.append({
                'category': category,
                'predicted_events': predicted_events,
            })

        return predictions

    def set_fitness(self, value): self.fitness = value

    def get_fitness(self): return self.fitness

    def print_rules(self):
        for category in self.categories:
            print(f'category {category.id}')
            print(f'with inside: {[self.element_pool[i].description for i in range(len(self.element_pool)) if self.element_pool[i].id in category.get_elements()]}')
            print('rules:')
            for trigger, effect in category.get_rules().items():
                print(f'{trigger} -> {effect}')

    def get_element_pool(self): return self.element_pool

    def get_fitness_adjustments(self):

        fitness_adjustment = 0
        objects_in_categories = {}

        for category in self.categories:
            fitness_adjustment += category.get_fitness_adjustments()
            objects = category.get_objects()

            for object in objects:
                if object.id in objects_in_categories.keys():
                    objects_in_categories[object.id] += 1
                else:
                    objects_in_categories[object.id] = 1
            
        for object_repetitions in objects_in_categories.values():

            if object_repetitions > 1:
                fitness_adjustment += pow(object_repetitions - 1, 4)

            elif object_repetitions == 0:
                fitness_adjustment += 10

        fitness_adjustment += pow(len(self.categories), 3)

        return fitness_adjustment