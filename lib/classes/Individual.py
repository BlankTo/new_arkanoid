import random
import itertools
import numpy as np

from .Category import Category
from .Element import Element
from .Event import Event
from .Object import Object
from .Rule import Rule
from ..utils import ID_creator


class Individual:

    def __init__(self, element_pool, event_pool, original: 'Individual' = None):
        
        self._element_pool = element_pool
        self._event_pool = event_pool

        if original is None:

            self.gen_obj_id = ID_creator().get_id
            self.gen_rule_id = ID_creator().get_id
            self.gen_cat_id = ID_creator().get_id

            self._objects = []
            self._rules = []
            self._categories = []

        else:

            current_obj_id, current_rule_id, current_cat_id = original.get_current_ids()
            self.gen_obj_id = ID_creator(current_obj_id).get_id
            self.gen_rule_id = ID_creator(current_rule_id).get_id
            self.gen_cat_id = ID_creator(current_cat_id).get_id

            self._objects = [Object(obj.id, obj.elements) for obj in original.objects]
            self._rules = [Rule(rule.id, rule.trigger, rule.effect) for rule in original.rules]
            self._categories = [Category(cat.id, [obj for obj in self._objects if obj.id in cat.objects], [rule for rule in self._rules if rule.id in cat.rules]) for cat in original.categories]

        self._fitness = 0

    @property
    def element_pool(self) -> list[Element]:
        return self._element_pool

    @property
    def event_pool(self) -> list[Event]:
        return self._event_pool

    @property
    def objects(self) -> list[Object]:
        return self._objects

    @property
    def rules(self) -> list[Rule]:
        return self._rules

    @property
    def categories(self) -> list[Category]:
        return self._categories

    @property
    def fitness(self):
        return self._fitness
    
    def __repr__(self):
        out = 'Objects:\n'
        if not self._objects: out += 'No Objects\n'
        for obj in self._objects:
            out += f'{obj}\n'
        out += '\nRules:\n'
        if not self._rules: out += 'No Rules\n'
        for rule in self._rules:
            out += f'{rule}\n'
        out += '\nCategories:\n'
        if not self._categories: out += 'No Categories\n'
        for cat in self._categories:
            out += f'{cat}\n'
        out += '\n'
        return out
    
    def get_current_ids(self):
        return self.gen_obj_id(), self.gen_rule_id(), self.gen_cat_id()

    def initialize(self, min_starting= 2, max_starting= 10) -> 'Individual':
        
        for _ in range(random.randint(min_starting, min([max_starting, len(self._element_pool)]))):
            self._objects.append(Object(self.gen_obj_id()).initialize(self._element_pool, self._objects))

        for _ in range(random.randint(min_starting, min([max_starting, pow(len(self._event_pool), 2)]))):
            self._rules.append(Rule(self.gen_rule_id()).initialize(self._event_pool, self._rules))

        for _ in range(random.randint(min_starting, min([max_starting, len(self._objects) * len(self._rules)]))):
            self._categories.append(Category(self.gen_cat_id()).initialize(self._objects, self._rules, self._categories))
        
        return self
    
    def set_all(self, objects, rules, categories):
        self._objects = objects
        self._rules = rules
        self._categories = categories
        return self
    
    def mutate(self) -> 'Individual':

        leno = len(self._objects)
        lenr = len(self._rules)
        lenc = len(self._categories)
        lene2 = pow(len(self._event_pool), 2)

        mutate_what_pool = []

        if leno < len(self._element_pool): mutate_what_pool.append('create_obj')
        if lenr < lene2: mutate_what_pool.append('create_rule')
        if lenc < (leno * lenr) and lenr > 0: mutate_what_pool.append('create_cat')
        if leno > 1:
            ok_objs: list[Object] = []
            for obj in self._objects:
                if len(obj.elements) > 1:
                    ok_objs.append(obj)
            if ok_objs:
                mutate_what_pool.append('move_elem')
                mutate_what_pool.append('divide_obj')
                pass
            mutate_what_pool.append('delete_obj')
            mutate_what_pool.append('fuse_obj')
        if lenc > 1:
            ok_cats: list[Category] = []
            for cat in self._categories:
                if len(cat.objects) > 1:
                    ok_cats.append(cat)
            if ok_cats:
                mutate_what_pool.append('move_obj')
                mutate_what_pool.append('divide_cat')
                pass
            mutate_what_pool.append('delete_cat')
            mutate_what_pool.append('fuse_cat')
        if lenr > 1: mutate_what_pool.append('delete_rule')
        if leno > 0: mutate_what_pool.append('mutate_obj')
        if lenc > 0: mutate_what_pool.append('mutate_cat')

        mutate_what = random.choice(mutate_what_pool)
        match mutate_what:

            case 'create_obj':
                #print('create_obj')
                new_obj = Object(self.gen_obj_id()).initialize(self._element_pool, self._objects)
                self._objects.append(new_obj)
                for cat in random.sample(self._categories, 1):
                    cat.add_object(new_obj)

            case 'create_rule':
                #print('create_rule')
                new_rule = Rule(self.gen_rule_id()).initialize(self._event_pool, self._rules)
                self._rules.append(new_rule)
                for cat in random.sample(self._categories, 1): # more than one ?
                    cat.add_rule(new_rule)

            case 'create_cat':
                #print('create_cat')
                if random.random() > 0.5:
                    self._categories.append(Category(self.gen_cat_id()).initialize(self._objects, self._rules, self._categories))
                else:
                    if (random.random() > 0.5 and self._objects) or (len(self._objects) >= len(self._element_pool)):
                        new_obj = random.choice(self._objects)
                    else:
                        new_obj = Object(self.gen_obj_id()).initialize(self.element_pool, self.objects)
                        self._objects.append(new_obj)
                    if (random.random() > 0.5 and self._rules) or (len(self._rules) >= lene2):
                        new_rule = random.choice(self._rules)
                    else:
                        new_rule = Rule(self.gen_rule_id()).initialize(self.event_pool, self._rules)
                        self._rules.append(new_rule)
                    self._categories.append(Category(self.gen_cat_id(), [new_obj], [new_rule]))

            case 'delete_obj':
                #print('delete_obj')
                obj_to_delete = random.choice(self._objects)
                self._objects.remove(obj_to_delete)
                cat_to_remove = []
                for cat in self._categories:
                    cat.remove_object(obj_to_delete)
                    if not cat.objects: cat_to_remove.append(cat)
                for cat in cat_to_remove: self._categories.remove(cat)
                if not self._categories: self._categories.append(Category(self.gen_cat_id()).initialize(self._objects, self._rules, self._categories))

            case 'delete_rule':
                #print('delete_rule')
                rule_to_delete = random.choice(self._rules)
                self._rules.remove(rule_to_delete)
                for cat in self._categories:
                    cat.remove_rule(rule_to_delete)

            case 'delete_cat':
                #print('delete_cat')
                self._categories.remove(random.choice(self._categories))

            case 'fuse_obj':
                #print('fuse_obj')
                objs_to_fuse = random.sample(self._objects, 2)
                self._objects.remove(objs_to_fuse[1])
                cat_to_remove = []
                for cat in self._categories:
                    cat.remove_object(objs_to_fuse[1])
                    if not cat.objects: cat_to_remove.append(cat)
                for cat in cat_to_remove: self._categories.remove(cat)
                objs_to_fuse[0].fuse(objs_to_fuse[1])
                if not self._categories: self._categories.append(Category(self.gen_cat_id()).initialize(self._objects, self._rules, self._categories))

            case 'fuse_cat':
                #print('fuse_cat')
                cats_to_fuse = random.sample(self._categories, 2)
                self._categories.remove(cats_to_fuse[1])
                cats_to_fuse[0].fuse(cats_to_fuse[1])

            case 'move_elem':
                from_obj = random.choice(ok_objs)
                elem_to_move = random.choice(from_obj.elements)
                to_obj = random.choice([obj for obj in self._objects if obj != from_obj])
                from_obj.remove_element(elem_to_move)
                to_obj.add_element(elem_to_move)

            case 'move_obj':
                from_cat = random.choice(ok_cats)
                obj_to_move = random.choice(from_cat.objects)
                to_cat = random.choice([cat for cat in self._categories if cat != from_cat])
                from_cat.remove_object(obj_to_move)
                to_cat.add_object(obj_to_move)

            case 'divide_obj':
                obj_to_mutate = random.choice(ok_objs)
                elem_to_move = random.choice(obj_to_mutate.elements) # only one
                obj_to_mutate.remove_element(elem_to_move)
                new_obj = Object(self.gen_obj_id(), [elem_to_move])
                self._objects.append(new_obj)
                for cat in self._categories:
                    if obj_to_mutate in cat.objects:
                        cat.add_object(new_obj)

            case 'divide_cat':
                cat_to_mutate = random.choice(ok_cats)
                obj_to_move = random.choice(cat_to_mutate.objects) # only one
                cat_to_mutate.remove_object(obj_to_move)
                if (random.random() > 0.5 and self._rules) or (len(self._rules) >= lene2):
                    new_rule = random.choice(self._rules)
                else:
                    new_rule = Rule(self.gen_rule_id()).initialize(self.event_pool, self._rules)
                    self._rules.append(new_rule)
                self._categories.append(Category(self.gen_cat_id(), [obj_to_move], [new_rule]))

            case 'mutate_obj':
                #print('mutate_obj')
                random.choice(self._objects).mutate(self._element_pool)

            case 'mutate_cat':
                #print('mutate_cat')
                random.choice(self._categories).mutate(self._objects, self._rules)

        return self

    def predict(self, events_per_frame):

        predicted_events = []

        for cat in self._categories:

            for current_events in events_per_frame:
                if current_events:

                    for current_event in current_events:

                        for cat_rule in cat.rules:
                            if cat_rule.trigger == current_event:

                                for cat_obj in cat.objects:

                                    for cat_obj_elem in cat_obj.elements:
                                        if current_event.subject == cat_obj_elem:
                                                
                                                predicted_events.append(Event(cat_rule.effect, current_event.subject))
        
        return predicted_events
    
    def rules_in_obj(self, obj):
        rules = []
        for cat in self._categories:
            if obj in cat.objects:
                for rule in cat.rules:
                    if rule not in rules:
                        rules.append(rule)
        return rules
    
    def rules_in_elem(self, elem):
        rules = []
        for cat in self._categories:
            if elem.id in cat.get_elements_id():
                for rule in cat.rules:
                    if rule not in rules:
                        rules.append(rule)
        return rules
    
    def elems_id_in_rules(self, rule):
        elems_id = []
        for cat in self._categories:
            if rule in cat.rules:
                elems_id.extend(cat.get_elements_id())
        return list(set(elems_id))
    
    def objs_in_rules(self, rule):
        objs = []
        for cat in self._categories:
            if rule in cat.rules:
                for obj in cat.objects:
                    if obj not in objs:
                        objs.append(obj)
        return objs
    
    def compute_fitness(self, events_per_frame: list[list[Event]], log= False) -> None: self.compute_fitness_4(events_per_frame, log)
    
    def compute_fitness_4(self, events_per_frame: list[list[Event]], log= False) -> None:

        score = 0

        elements_correctness = {elem.id: {rule.id: [0, 0, False] for rule in self._rules} for elem in self._element_pool}
        objects_correctness = {obj.id: {rule.id: [0, 0, False] for rule in self._rules} for obj in self._objects}
        categories_correctness = {cat.id: {rule.id: [0, 0] for rule in self._rules} for cat in self._categories}
        all_correct_cats = 0

        rule_usage = {(et1.id, et2.id, elem.id): [False, False] for et1 in self._event_pool for et2 in self._event_pool for elem in self._element_pool}

        for cat in self._categories:

            cat_is_correct = True

            for frame_id in range(len(events_per_frame) - 1):

                next_frame_events = events_per_frame[frame_id + 1]

                for current_event in events_per_frame[frame_id]:

                    if current_event.subject in next_frame_events:
                        for nfe in next_frame_events:
                            if nfe.subject == current_event.subject:
                                rule_usage[current_event.event_type.id, nfe.event_type.id, current_event.subject.id][0] = True

                    for cat_rule in cat.rules:
                        
                        cat_used = False
                        cat_rule_is_correct = True

                        if cat_rule.trigger == current_event:

                            for cat_obj in cat.objects:

                                cat_obj_used = False
                                obj_is_correct = True

                                objects_correctness[cat_obj.id][cat_rule.id][2] = True

                                for cat_obj_elem in cat_obj.elements:
                                    
                                    elements_correctness[cat_obj_elem.id][cat_rule.id][2] = True

                                    if current_event.subject == cat_obj_elem:

                                        cat_obj_used, cat_used = True, True
                                        rule_usage[cat_rule.trigger.id, cat_rule.effect.id, current_event.subject.id][1] = True

                                        if (cat_rule.effect, current_event.subject) in next_frame_events:
                                            elements_correctness[cat_obj_elem.id][cat_rule.id][0] += 1
                                        else:
                                            cat_is_correct, obj_is_correct, cat_rule_is_correct = False, False, False
                                            elements_correctness[cat_obj_elem.id][cat_rule.id][1] += 1

                                if cat_obj_used:
                                    pass
                                    
                                    if obj_is_correct:
                                        objects_correctness[cat_obj.id][cat_rule.id][0] += 1
                                        pass

                                    else:
                                        objects_correctness[cat_obj.id][cat_rule.id][1] += 1
                                        pass


                        if cat_used:
                            if cat_rule_is_correct:
                                categories_correctness[cat.id][cat_rule.id][0] += 1
                                pass
                            
                            else:
                                categories_correctness[cat.id][cat_rule.id][1] += 1
                                pass

            if cat.rules and cat_is_correct:
                all_correct_cats += 1


        for elem in self._element_pool:
            if log: print(f'elem: {elem}')

            objs = []
            objs_rules = {}
            for obj in self._objects:
                if elem in obj.elements:
                    objs.append(obj.id)
                    for cat in self._categories:
                        if obj in cat.objects:
                            for rule in cat.rules:
                                if (rule.id, obj.id) in objs_rules.keys(): objs_rules[rule.id, obj.id] += 1
                                else: objs_rules[rule.id, obj.id] = 1

            cats = []
            cats_rules = {}
            for cat in self._categories:
                if elem.id in cat.get_elements_id():
                    cats.append(cat.id)
                    for rule in cat.rules:
                        if (rule.id, cat.id) in cats_rules.keys(): cats_rules[rule.id, cat.id] += 1
                        else: cats_rules[rule.id, cat.id] = 1

            if objs:
                if len(objs) > 1:
                    score -= pow(2, len(objs) - 1) # penalty for same element in different objects
                    if log: print(f'elem repeted in objects: {len(objs)} -> penalty: -{pow(2, len(objs) - 1)}')
            else:
                score -= 10 # penalty for elem not present in any object
                if log: print(f'elem not in any obj -> penalty: -10')

            if log and objs_rules: print('objs rep')
            for (rule_id, obj_id), rep in objs_rules.items():
                if rep > 1:
                    score -= pow(5, rep - 1) # penalty for same element in different objects with same rule applied
                    if log: print(f'{(rule_id, obj_id, rep)} -> penalty: -{pow(10, rep - 1)}')
                elif log: print(f'{(rule_id, obj_id, rep)} -> no penalty')

            if cats:
                if len(cats) > 1:
                    score -= pow(2, len(cats) - 1) # penalty for same element in different categories
                    if log: print(f'elem repeted in categories: {len(cats)} -> penalty: -{pow(2, len(cats) - 1)}')
            else:
                score -= 10 # penalty for elem not present in any category
                if log: print(f'elem not in any cat -> penalty: -10')

            if log and cats_rules: print('cats rep')
            for (rule_id, cat_id), rep in cats_rules.items():
                if rep > 1:
                    score -= pow(2, rep - 1) # penalty for same element in different categories with same rule applied
                    if log: print(f'{(rule_id, cat_id, rep)} -> penalty: -{pow(10, rep - 1)}')
                elif log: print(f'{(rule_id, cat_id, rep)} -> no penalty')

            for rule in self._rules:
                ec = elements_correctness[elem.id][rule.id]
                if ec[2]:
                    if ec[1] > 0:
                        score -= 1 # penalty for (elem, rule) that resulted wrong at least one time
                        if log: print(f'({elem}, {rule}): {ec} -> wrong -> penalty: -1')
                    elif ec[0] > 0:
                        score += 1 # bonus for (elem, rule) always correct
                        if log: print(f'({elem}, {rule}): {ec} -> all_correct -> bonus: +1')
                    else:
                        score -= 1 # penalty for (elem, rule) in same cat but never used
                        if log: print(f'({elem}, {rule}): {ec} -> not_used -> penalty: -1')

        for obj in self._objects:
            if log: print(f'obj_{obj.id}')

            if len(obj.elements) > 1:
                score -= len(obj.elements) - 1 # penalty for number of elements per object
                if log: print(f'n_elems: {len(obj.elements)} -> penalty: -{len(obj.elements) - 1}')

            if len([cat.id for cat in self._categories if obj in cat.objects]) == 0:
                score -= 1 # penalty for object not present in any category
                if log: print(f'object not present in any categories -> penalty: -{len(obj.elements)}')
            
            for rule in self._rules:
                oc = objects_correctness[obj.id][rule.id]

                if oc[2]:
                    if oc[1] > 0:
                        score -= 1 # penalty for (obj, rule) that resulted wrong at least one time
                        if log: print(f'({obj}, {rule}): {oc} -> wrong -> penalty: -1')
                    elif oc[0] > 0:
                        score += 2 # bonus for (obj, rule) always correct
                        if log: print(f'({obj}, {rule}): {oc} -> all_correct -> bonus: +2')
                    else:
                        score -= 1 # penalty for (obj, rule) in same cat but never used
                        if log: print(f'({obj}, {rule}): {oc} -> not_used -> penalty: -1')

        for cat in self._categories:
            if log: print(f'cat_{cat.id}')
            if log: print(f'len: {len(cat.objects)}')

            score -= len(cat.objects) # penalty for number of objects in a category
            if log: print(f'n_objs: {len(cat.objects)} -> penalty: -{len(cat.objects)}')

            for rule in self._rules:
                if rule in cat.rules:
                    cc = categories_correctness[cat.id][rule.id]

                    if cc[1] > 0:
                        score -= 1 # penalty for (cat, rule) that resulted wrong at least one time
                        if log: print(f'(cat_{cat.id}, {rule}): {cc} -> wrong -> penalty: -1')
                    elif cc[0] > 0:
                        score += 1 # bonus for (cat, rule) always correct
                        if log: print(f'(cat_{cat.id}, {rule}): {cc} -> all_correct -> bonus: +1')
                    else:
                        score -= 1 # penalty for (cat, rule) in same cat but never used
                        if log: print(f'(cat_{cat.id}, {rule}): {cc} -> not_used -> penalty: -1')

        score += all_correct_cats
        if log: print(f'all_correct_cats: {all_correct_cats} -> bonus: +{all_correct_cats}')

        score -= len(self._rules) # penalty for number of rules
        if log: print(f'n_rules: {len(self._rules)} -> penalty: -{len(self._rules)}')

        for rule in self._rules:
            n_cat = len([cat.id for cat in self._categories if rule in cat.rules])
            if n_cat > 1:
                score -= pow(2, n_cat)
                if log: print(f'({rule}) in {n_cat} categories -> penalty: -{pow(2, n_cat)}')
            else:
                if log: print(f'({rule}) in {n_cat} categories -> no penalty')

        rule_usage[current_event.event_type.id, nfe.event_type.id, current_event.subject.id][0] = True

        for should_be_rule, is_rule in rule_usage.values():

            if should_be_rule and is_rule:
                score += 1

            elif should_be_rule or is_rule:
                score -= 1

        self._fitness = score


    
    def compute_fitness_3(self, events_per_frame: list[list[Event]], log= False) -> None:

        score = 0

        score -= len(self._categories) * 10
        score -= len(self._objects)

        for cat in self._categories: score -= len(cat.objects)
        for obj in self._objects: score -= len(obj.elements)

        #rule_usage_matrix = [[[[[0, 0, False] for _ in range(len(self._element_pool))] for _ in range(len(self._objects))] for _ in range(len(self._categories))] for _ in range(len(self._rules))]
        
        for rep in [sum([bool(obj in cat.objects) for cat in self._categories]) for obj in self._objects]:
            if rep == 0: score -= 10
            elif rep > 1: score -= (rep - 1)

        for rep in [sum([bool(elem.id in cat.get_elements_id()) for cat in self._categories]) for elem in self._element_pool]:
            if rep == 0: score -= 10
            elif rep > 1: score -= (rep - 1)

        for rep in [sum([bool(rule.id in cat.rules) for cat in self._categories]) for rule in self._rules]:
            if rep > 1: score -= (rep - 1)
        
        #for i_rule, rule in enumerate(self._rules):
        for rule in self._rules:

            #for i_cat, cat in enumerate(self._categories):
            for cat in self._categories:
                if rule in cat.rules:

                    #for i_obj, obj in enumerate(self._objects):
                    for obj in self._objects:
                        if obj in cat.objects and obj in self.objs_in_rules(rule):

                            #for i_elem, elem in enumerate(self._element_pool):
                            for elem in self._element_pool:
                                if elem.id in self.elems_id_in_rules(rule):

                                    for frame_id in range(len(events_per_frame) - 1):

                                        for current_event in events_per_frame[frame_id]:
                                            if current_event.event_type == rule.trigger and current_event.subject == elem:
                                                
                                                correct = False
                                                #rule_usage_matrix[i_rule][i_cat][i_obj][i_elem][2] = True

                                                for next_frame_event in events_per_frame[frame_id + 1]:
                                                    if next_frame_event.event_type == rule.effect and next_frame_event.subject == elem:
                                                        
                                                        score += 1
                                                        correct = True
                                                        #rule_usage_matrix[i_rule][i_cat][i_obj][i_elem][0] += 1

                                                    #elif next_frame_event.subject == elem: # missed rule

                                                if not correct:

                                                    score -= 1
                                                    #rule_usage_matrix[i_rule][i_cat][i_obj][i_elem][1] += 1

#        rule_usage_matrix = np.array(rule_usage_matrix)
#        #print(rule_usage_matrix.shape)
#
#        for i_cat, i_obj in itertools.product(range(len(self._categories)), range(len(self._objects))):
#            tmp = rule_usage_matrix[:, i_cat, i_obj, :, :]
#            if tmp.sum() != 0:
#                rep = tmp[:, :, 2].sum()
#                if rep == 0: score -= 10
#                elif rep > 0: score -= (rep - 1)
#                else:
#                    sw = tmp[:, :, 1].sum()
#                    if sw > 0: score -= sw
#                    else:
#                        sc = tmp[:, :, 0].sum()
#                        if sc > 0: score += sc
#                        else: score -= 10
#
#        for i_cat, i_elem in itertools.product(range(len(self._categories)), range(len(self._element_pool))):
#            tmp = rule_usage_matrix[:, i_cat, :, i_elem, :]
#            if tmp.sum() != 0:
#                rep = tmp[:, :, 2].sum()
#                if rep == 0: score -= 10
#                elif rep > 0: score -= (rep - 1)
#                else:
#                    sw = tmp[:, :, 1].sum()
#                    if sw > 0: score -= sw
#                    else:
#                        sc = tmp[:, :, 0].sum()
#                        if sc > 0: score += sc
#                        else: score -= 10
#
#        for i_obj, i_rule in itertools.product(range(len(self._objects)), range(len(self._rules))):
#            tmp = rule_usage_matrix[i_rule, :, i_obj, :, :]
#            if tmp.sum() != 0:
#                rep = tmp[:, :, 2].sum()
#                if rep == 0: score -= 10
#                elif rep > 0: score -= (rep - 1)
#                else:
#                    sw = tmp[:, :, 1].sum()
#                    if sw > 0: score -= sw
#                    else:
#                        sc = tmp[:, :, 0].sum()
#                        if sc > 0: score += sc
#                        else: score -= 10
#
#        for i_elem, i_rule in itertools.product(range(len(self._element_pool)), range(len(self._rules))):
#            tmp = rule_usage_matrix[i_rule, :, :, i_elem, :]
#            if tmp.sum() != 0:
#                rep = tmp[:, :, 2].sum()
#                if rep == 0: score -= 10
#                elif rep > 0: score -= (rep - 1)
#                else:
#                    sw = tmp[:, :, 1].sum()
#                    if sw > 0: score -= sw
#                    else:
#                        sc = tmp[:, :, 0].sum()
#                        if sc > 0: score += sc
#                        else: score -= 10
        
        #print(self)
        #print(score)
        self._fitness = score

        #exit()

    
    def compute_fitness_2(self, events_per_frame: list[list[Event]], log= False) -> None:

        score = 0

        score -= len(self._rules)
        score -= len(self._objects)
        score -= len(self._categories)

        element_repetitions_in_objects = [sum([bool(elem in obj.elements) for obj in self._objects]) for elem in self._element_pool]
        for erio in element_repetitions_in_objects:
            if erio > 1: score -= pow(erio - 1, 2)

        object_repetitions_in_categories = [sum([bool(obj in cat.objects) for cat in self._categories]) for obj in self._objects]
        for oric in object_repetitions_in_categories:
            if oric > 1: score -= pow(oric - 1, 2)

        element_cat_rule_usage = {elem.id: 0 for elem in self._element_pool}
        for cat1, cat2 in itertools.combinations(self.categories, 2):
            for rule1, rule2 in itertools.product(cat1.rules, cat2.rules):
                if rule1 == rule2:
                    for elem1_id, elem2_id in itertools.product(cat1.get_elements_id(), cat2.get_elements_id()):
                        if elem1_id == elem2_id:
                            element_cat_rule_usage[elem1_id] += 1

        rule_cat_elem_repetitions = [x for x in element_cat_rule_usage.values() if x > 1]

        for rcer in rule_cat_elem_repetitions: score -= pow(10, rcer)

        #rules_usage = {rule.id: {'correct': 0, 'wrong': 0, 'subject_categories': [], 'subject_objects': [], 'subject_elements': []} for rule in self._rules}

        #element_correctness_in_objects = {obj.id: {'correct': 0, 'wrong': 0, 'all_correct': 0} for obj in self._objects}
        #element_correctness_in_categories = {cat.id: {'correct': 0, 'wrong': 0, 'all_correct': 0} for cat in self._categories}

        for cat in self._categories:

            cat_is_correct = False

            for frame_id in range(len(events_per_frame) - 1):

                current_events = events_per_frame[frame_id]

                if current_events:

                    next_frame_events = events_per_frame[frame_id + 1]

                    for current_event in current_events:

                        for cat_rule in cat.rules:
                            
                            #cat_used = False

                            if cat_rule.trigger == current_event:

                                for cat_obj in cat.objects:

                                    cat_obj_used = False
                                    obj_is_correct = False

                                    for cat_obj_elem in cat_obj.elements:

                                        if current_event.subject == cat_obj_elem:

                                            cat_obj_used = True
                                                
                                            #if cat_obj_elem not in rules_usage[cat_rule.id]['subject_elements']:
                                            #    rules_usage[cat_rule.id]['subject_elements'].append(cat_obj_elem.id)

                                            if (cat_rule.effect, current_event.subject) in next_frame_events:
                                                #score += 1
                                                cat_is_correct, obj_is_correct = True, True
                                                #rules_usage[cat_rule.id]['correct'] += 1
                                                #element_correctness_in_objects[cat_obj.id]['correct'] += 1
                                                #element_correctness_in_categories[cat.id]['correct'] += 1
                                            else:
                                                score -= 1
                                                #rules_usage[cat_rule.id]['wrong'] += 1
                                                #element_correctness_in_objects[cat_obj.id]['wrong'] += 1
                                                #element_correctness_in_categories[cat.id]['wrong'] += 1

                                    if cat_obj_used:

                                        #cat_used = True

                                        #if cat_obj not in rules_usage[cat_rule.id]['subject_objects']:
                                        #    rules_usage[cat_rule.id]['subject_objects'].append(cat_obj.id)
                                            

                                        if obj_is_correct:
                                            #element_correctness_in_objects[cat_obj.id]['all_correct'] += 1
                                            if cat.rules:
                                                score += len(cat_obj.elements) * 10 # 10

                            #if cat_used:
                            #    if cat not in rules_usage[cat_rule.id]['subject_categories']:
                            #        rules_usage[cat_rule.id]['subject_categories'].append(cat.id)

            if cat_is_correct:
                #element_correctness_in_categories[cat.id]['all_correct'] += 1
                if cat.rules:
                    score += len(cat.objects) # 1

        #for ru in rules_usage.values():
        #    if ru['wrong'] > 0: score -= 10
        #    elif ru['correct'] > 0: score += 100
        #    else: score -= 10

        self._fitness = score
        return

        for obj in self._objects:
            score -= len(obj.elements)

        for rule_usage in rules_usage.values():

            if rule_usage['wrong'] > 0:
                score -= rule_usage['wrong'] * 10

            elif rule_usage['correct'] > 0:
                score += 10

            else: score -= 100

            element_rule_repetition = {elem.id: 0 for elem in self._element_pool}
            for subject_element_id in rule_usage['subject_elements']:
                element_rule_repetition[subject_element_id] += 1

            for elem_rep in element_rule_repetition.values():
                if elem_rep == 0: score -= 100
                elif elem_rep > 1: score -= (elem_rep - 1)

            object_rule_repetition = {obj.id: 0 for obj in self._objects}
            for subject_object_id in rule_usage['subject_objects']:
                object_rule_repetition[subject_object_id] += 1

            for obj_rep in object_rule_repetition.values():
                if obj_rep == 0: score -= 100
                elif obj_rep > 1: score -= (obj_rep - 1)

            category_rule_repetition = {cat.id: 0 for cat in self._categories}
            for subject_category_id in rule_usage['subject_categories']:
                category_rule_repetition[subject_category_id] += 1

            for cat_rep in category_rule_repetition.values():
                if cat_rep == 0: score -= 100
                elif cat_rep > 1: score -= (cat_rep - 1)

        self._fitness = score

    def compute_fitness_1(self, events_per_frame: list[list[Event]], log= False) -> None:

        score = 0
        rule_usage = [[[-1 for _ in range(len(cat.get_elements_id()))] for _ in range(len(cat.rules))] for cat in self._categories]

        for frame_id in range(len(events_per_frame) - 1):

            events = events_per_frame[frame_id]
            next_frame_events = events_per_frame[frame_id + 1]

            if events and next_frame_events:

                for i_cat, cat in enumerate(self._categories):

                    elements_id = cat.get_elements_id()
            
                    for event in events:

                        if event.subject in elements_id:

                            if event.event_type in cat.rules:

                                for i, rule in enumerate(cat.rules):

                                    trigger = rule.trigger
                                    effect = rule.effect

                                    if event.event_type == trigger:
                                        element_idx = None
                                        for elem_i, elem_id in enumerate(elements_id):
                                            if elem_id == event.subject:
                                                element_idx = elem_i
                                                break

                                        rule_usage[i_cat][i][element_idx] = 0 # rule is used on element

                                        # check against next_frame_events

                                        correct = False

                                        for nfe in next_frame_events:

                                            if effect == nfe.event_type and event.subject == nfe.subject:
                                                correct = True
                                                break

                                        if correct:
                                            #print(f'correct: {[(e.event_type, e.subject) for e in events]} -> {(predicted_event.event_type, predicted_event.subject)}')
                                            if rule_usage[i_cat][i][element_idx] != 2: # not wrong
                                                rule_usage[i_cat][i][element_idx] = 1
                                        else:
                                            #print(f'wrong: {[(e.event_type, e.subject) for e in events]} -> {(predicted_event.event_type, predicted_event.subject)}')
                                            rule_usage[i_cat][i][element_idx] = 2

        for rule_usage_cat in rule_usage:

            rule_usage_list = list(itertools.chain.from_iterable(rule_usage_cat))
            score -= rule_usage_list.count(-1) * 1000 # penalty for each element to with a rule is never applied
            score -= rule_usage_list.count(2) * 1000 # penalty for each element to with a rule is wrongly applied
            score += rule_usage_list.count(1) * 10 # bonus for each element to with a rule is correctly applied


        objects_in_categories = {obj.id: 0 for obj in self._objects}
        elements_in_objects = {elem.id: 0 for elem in self._element_pool}

        for obj in self._objects:
            
            score -= len(obj.elements) *100 # penalty for too many elements in an object

            for elem in obj.elements:
                elements_in_objects[elem.id] += 1
            
        for element_repetitions in elements_in_objects.values():

            if element_repetitions > 1:
                score -= pow(1000, element_repetitions - 1) # penalty for same element in different objects
                pass

            elif element_repetitions == 0:
                score -= 100000000 # penalty for element not present in any object
                pass


        for cat in self._categories:
            
            score -= len(cat.objects) # penalty for too many objects in a category

            for obj in cat.objects:
                if obj.id in objects_in_categories.keys():
                    objects_in_categories[obj.id] += 1
                else:
                    raise Exception(f'misaligned objects error - get_fitness_adjustments\nobjects:{self._objects}\nobj: {obj}')

        for object_repetitions in objects_in_categories.values():

            if object_repetitions > 1:
                score -= pow(10, object_repetitions - 1) # penalty for objects repeated in many categories
                pass

            elif object_repetitions == 0:
                score -= 100000 # penalty for object not present in any category

        score -= len(self._categories) # penalty for too many categories

        self._fitness = score