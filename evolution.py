import math
import time
import random
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

    #element_pool = individual.get_element_pool()

    for frame_id in range(len(events_per_frame) - 1):

        events = events_per_frame[frame_id]

        next_frame_events = events_per_frame[frame_id + 1]

        if len(next_frame_events) > 0:

            predictions = individual.predict(events)

            for pred in predictions:

                #category = pred['category']
                predicted_events = pred['predicted_events']

                if len(predicted_events) > 0:

                    #print('---------------------------------------------------------------------')
                    #print(f'cat_id: {category.id}')
                    #print(category.get_elements())
                    #print(f"current_frame_events: {[(e.event_type, e.subject) for e in events]}")
                    #print(f"next_frame_events: {[(e.event_type, e.subject) for e in next_frame_events]}")
                    #print(f"predicted_events: {[(e.event_type, e.subject) for e in predicted_events]}")

                    n_correct_predictions = 0
                    n_wrong_predictions = 0

                    for predicted_event in predicted_events:

                        correct = False

                        for event in next_frame_events:

                            if predicted_event.event_type == event.event_type and predicted_event.subject == event.subject:
                                correct = True
                                break

                        if correct:
                            #print(f'correct: {[(e.event_type, e.subject) for e in events]} -> {(predicted_event.event_type, predicted_event.subject)}')
                            n_correct_predictions += 1
                        else:
                            #print(f'wrong: {[(e.event_type, e.subject) for e in events]} -> {(predicted_event.event_type, predicted_event.subject)}')
                            n_wrong_predictions += 1

                    score += n_correct_predictions * 1000 - n_wrong_predictions * 10000# - (len(next_frame_events) - n_correct_predictions) * 1
                
                #else: score -= len(next_frame_events) * 1

    score -= individual.get_fitness_adjustments() * 1

    return score


def selection(population, num_selected):
    return sorted(population, key=lambda ind: ind.get_fitness(), reverse=True)[:num_selected]


class EvolutionaryAlgorithm:
    def __init__(self, elements, events_per_frame, event_pool):
        self.element_pool = elements
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

        for gen_id in range(max_generations):

            if gen_id > 0:
                eta = ((time.time() - starting_time) / gen_id) * (max_generations - gen_id)
                print(f"\r{gen_id}/{max_generations} - eta: {format_time(eta)}                  ", end= '')
            else:
                print(f"{gen_id}/{max_generations}", end= '')
            #print(f'generation {gen_id}')

            # Evaluation
            self.evaluation()

            # Selection
            survivors = selection(self.population, num_individuals // 5)

            best_fitness = self.get_winner().get_fitness()
            if best_fitness > self.old_best:
                self.old_best = best_fitness
                print(f'\rgeneration {gen_id}                                   ', end= '')
                print(f'\nnew best fitness: {best_fitness}')
                print(f"\n{gen_id}/{max_generations}                      ", end= '')
                #print(f'eta: {((time.time() - starting_time) / (gen_id + 1)) * (max_generations - gen_id)}')

            # Crossover and Mutation
            offspring = []

            # add the survivors directly or not?
            #offspring.extend(survivors)
            offspring.append(survivors[0])

            for survivor in survivors:
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

            # TODO add termination conditions

        print(f"\rTotal run time: {format_time(time.time() - starting_time)}", end= '')
        print('\n-------------------------------------------')

    def get_winner(self):
        return sorted(self.population, key= lambda ind: ind.get_fitness(), reverse= True)[0]