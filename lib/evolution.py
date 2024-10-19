import math
import time
import random

from .classes import Individual
from .utils import ID_creator, format_time


class EvolutionaryAlgorithm:

    def __init__(self, element_pool, events_per_frame, event_pool):

        self.element_pool = element_pool
        self.events_per_frame = events_per_frame
        self.event_pool = event_pool

        self.population = []

        self.get_object_id = ID_creator().get_id
        self.get_category_id = ID_creator().get_id
        self.get_rule_id = ID_creator().get_id

        self.old_best = - math.inf        

    def run(self, max_generations= 100, num_individuals= 100, patience= None, num_survivors= None) -> None:

        # initialize population
        
        self.population = [Individual(self.element_pool, self.event_pool).initialize() for _ in range(num_individuals)]

        for ind in self.population:
            for cat in ind.categories:
                if len(cat.objects) == 0:
                    print('initialization init')
                    print(cat)
                    exit()

        # setting loop config

        starting_time = time.time()

        if patience is None:
            patience = max_generations // 10
            if patience < 100: patience = 100

        if num_survivors is None: num_survivors = num_individuals // 5

        # evolution loop start

        for gen_id in range(max_generations):

            # print messages

            if gen_id > 0: print(f"\r{gen_id}/{max_generations} - eta: {format_time((((time.time() - starting_time) / gen_id) * (max_generations - gen_id)) * 2)}                  ", end= '')
            else: print(f"{gen_id}/{max_generations}", end= '')

            # Evaluation

            for individual in self.population: individual.compute_fitness(self.events_per_frame)

            # Selection

            survivors = sorted(self.population, key= lambda ind: ind.fitness, reverse= True)[:num_survivors]

            #print fitness improvement

            best_fitness = survivors[0].fitness
            if best_fitness > self.old_best:

                last_best_gen = gen_id
                self.old_best = best_fitness
                
                print(f'\rgeneration {gen_id}                                   ', end= '')
                print(f'\nnew best fitness: {best_fitness}')
                if gen_id > 0: print(f"\n{gen_id}/{max_generations} - eta: {format_time((((time.time() - starting_time) / gen_id) * (max_generations - gen_id)) * 2)}                      ", end= '')
                else: print(f"\n{gen_id}/{max_generations}                      ", end= '')

            ok = True
            try:
                # Repopulation

                offspring: list[Individual] = []

                # add the survivors untouched or not ?

                offspring.extend(survivors) # directly
                #offspring.append(survivors[0]) # only the best one

                # one garanteed mutation per survivor ?

                for survivor in survivors:
                    survivor_clone = Individual(self.element_pool, self.event_pool, survivor).mutate() # clone and mutate one time
                    for _ in range(random.randint(0, 5)): survivor_clone.mutate() # more random mutations ?
                    offspring.append(survivor_clone)

                # Mutation

                while len(offspring) < len(self.population):
                    offspring.append(Individual(self.element_pool, self.event_pool, random.choice(survivors)).mutate())
            
            except KeyboardInterrupt:
                print('evolution stopped by user request')
                ok = False

            # Replace old population with offspring
            if (gen_id < max_generations - 1) and ok:
                self.population = offspring

            # Termination conditions

            if ((gen_id - last_best_gen) > patience) or not ok:
                print('terminated for lack of patience')
                break

        print(f"\rTotal run time: {format_time(time.time() - starting_time)}", end= '')
        print('\n-------------------------------------------')

    def get_winner(self) -> Individual:
        return sorted(self.population, key= lambda ind: ind.fitness, reverse= True)[0]