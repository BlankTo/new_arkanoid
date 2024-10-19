import math
import time
import random
import itertools

from classes import ID_creator, Individual


def format_time(time_in_sec):
    hours, remainder = divmod(time_in_sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0: return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0: return f"{int(minutes)}m {int(seconds)}s"
    else: return f"{int(seconds)}s"


def fitness(individual, events_per_frame):

    score = 0

    individual.reset_rule_usage()

    for frame_id in range(len(events_per_frame) - 1):

        events = events_per_frame[frame_id]
        next_frame_events = events_per_frame[frame_id + 1]

        if events and next_frame_events:
            individual.predict_and_check(events, next_frame_events)

    for cat in individual.get_categories():

        rule_usage_list = list(itertools.chain.from_iterable(cat.get_rule_usage()))
        score -= rule_usage_list.count(-1) * 1000 # penalty for each element to with a rule is never applied
        score -= rule_usage_list.count(2) * 1000 # penalty for each element to with a rule is wrongly applied
        score += rule_usage_list.count(1) * 10 # bonus for each element to with a rule is correctly applied

    score -= individual.get_fitness_adjustments() * 1

    return score


def selection(population, num_selected):
    return sorted(population, key=lambda ind: ind.get_fitness(), reverse= True)[:num_selected]


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

    def initialize_population(self, num_individuals):

        population = []
        for _ in range(num_individuals):
            population.append(Individual(self.get_object_id, self.get_category_id).randomize(self.element_pool, self.event_pool))
        self.population = population

    def evaluation(self):

        for individual in self.population:
            individual.set_fitness(fitness(individual, self.events_per_frame))

    def run(self, max_generations= 100, num_individuals= 100):

        self.initialize_population(num_individuals)

        starting_time = time.time()

        patience = max_generations // 10
        if patience < 100: patience = 100

        for gen_id in range(max_generations):

            if gen_id > 0:
                eta = ((time.time() - starting_time) / gen_id) * (max_generations - gen_id)
                eta *= 2
                print(f"\r{gen_id}/{max_generations} - eta: {format_time(eta)}                  ", end= '')
            else:
                print(f"{gen_id}/{max_generations}", end= '')

            # Evaluation
            self.evaluation()

            # Selection
            survivors = selection(self.population, num_individuals // 5)

            #print fitness improvement
            best_fitness = self.get_winner().get_fitness()
            if best_fitness > self.old_best:
                last_best_gen = gen_id
                self.old_best = best_fitness
                print(f'\rgeneration {gen_id}                                   ', end= '')
                print(f'\nnew best fitness: {best_fitness}')
                if gen_id > 0:
                    eta = ((time.time() - starting_time) / gen_id) * (max_generations - gen_id)
                    eta *= 2
                    print(f"\n{gen_id}/{max_generations} - eta: {format_time(eta)}                      ", end= '')
                else:
                    print(f"\n{gen_id}/{max_generations}                      ", end= '')

            # Crossover and Mutation
            offspring = []

            # add the survivors directly or not?
            offspring.extend(survivors) # directly
            #offspring.append(survivors[0]) # only the best one

            for survivor in survivors: # one garanteed mutation per survivor
                offspring.append(survivor.mutate())

            while len(offspring) < len(self.population):

                #if random.random() > 0.7: # Mutation
                
                    offspring.append(random.choice(survivors).mutate())

                #else: # Crossover
                #    parents = random.sample(survivors, 2)
                #    offspring.append(parents[0].crossover(parents[1]))

            # Replace old population with offspring
            if gen_id < max_generations - 1:
                self.population = offspring

            # Termination conditions

            if (gen_id - last_best_gen) > patience:
                print('terminated for lack of patience')
                break

        print(f"\rTotal run time: {format_time(time.time() - starting_time)}", end= '')
        print('\n-------------------------------------------')

    def get_winner(self):
        return sorted(self.population, key= lambda ind: ind.get_fitness(), reverse= True)[0]