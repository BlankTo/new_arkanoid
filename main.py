import os
import pickle

from lib.classes import Element, EventType, Event
from lib.evolutionary_algorithm import EvolutionaryAlgorithm


## Retrieve log

log_file_name = None
#log_file_name = 'arkanoid_log_17_10_2024_17_47_51.pkl'
#log_file_name = 'arkanoid_log_19_10_2024_19_28_17.pkl' # first two are base game
#log_file_name = 'arkanoid_log_20_10_2024_15_42_56.pkl' # added game_end
#log_file_name = 'arkanoid_log_20_10_2024_16_31_59.pkl' # added change_color
log_file_name = 'arkanoid_log_20_10_2024_16_48_34.pkl' # added lose game if bottom hit

if log_file_name is None: # use last saved

    log_files_name = os.listdir('logs/arkanoid_logs')
    if not log_files_name: raise Exception('no saved logs')
    log_file_name = sorted(log_files_name, reverse= True)[0]

log_file_path = f'logs/arkanoid_logs/{log_file_name}'
with open(log_file_path, 'rb') as log_file:
    log = pickle.load(log_file)

print(f'{log_file_path} loaded')


## Create element_pool and event_pool

events_per_frame = []
event_pool = {}
elements_per_frame = []
element_pool = {}
event_type_id = 0

for frame in log:
    frame_id = frame['frame_id']

    elements = []
    for description, elem in frame['elements'].items():

        if elem['id'] in element_pool.keys():
            elements.append(element_pool[elem['id']])

        else:
            new_elem = Element(elem['id'], description, None)
            element_pool[elem['id']] = new_elem
            elements.append(new_elem)

    elements_per_frame.append(elements)

    events = []
    for event in frame['events']:
        description = event['description']
        subject = event['subject']

        #if subject: # TODO implement NoElement Element and assign it to 0 id
        if True:

            if description not in event_pool.keys():
                event_pool[description] = EventType(event_type_id, description)
                event_type_id += 1
                
            events.append(Event(event_pool[description], element_pool[subject]))
    
    events_per_frame.append(events)

element_pool: list[Element] = list(element_pool.values())
event_pool: list[EventType] = list(event_pool.values())

print('\n-------------------------------------\nelement pool:\n')
print(element_pool)
print('\n-------------------------------------\nevent pool:\n')
print(event_pool)
print('\n-------------------------------------')

#exit(0)

#for i in range(1000):
#    print(events_per_frame[i])
#exit()

#for i in range(1000):
#    print(elements_per_frame[i])
#exit()

## to check fitness on custom individuals

if False:
    from lib.classes import Individual, Object, Rule, Category

    paddle = None
    ball = None
    bricks = []
    walls = []
    for i, elem in enumerate(element_pool):
        if elem == 'ball':
            ball = Object(666, [elem])
        if elem == 'paddle_center':
            paddle = Object(667, [elem])
        if 'brick' in elem.description:
            bricks.append(Object(668 + i, [elem]))
        if 'wall' in elem.description:
            walls.append(Object(768 + i, [elem]))

    collision = None
    bounce = None
    disappearance = None
    for event_type in event_pool:
        if event_type == 'collision': collision = event_type
        if event_type == 'bounce': bounce = event_type
        if event_type == 'disappearance': disappearance = event_type

    ball_rule = Rule(666, collision, bounce)
    bricks_rule = Rule(667, collision, disappearance)

    ball_cat = Category(666, [ball], [ball_rule])
    bricks_cat = Category(667, bricks, [bricks_rule])
    others_cat = Category(668, [paddle] + walls, [])

    my_cat = Individual(element_pool, event_pool).set_all([paddle, ball] + bricks + walls, [ball_rule, bricks_rule], [ball_cat, bricks_cat, others_cat])
    
    print('my_cat:')
    print(my_cat)
    my_cat.compute_fitness(events_per_frame, log= True)
    print(f'my_cat_fitness: {my_cat.fitness}') # 81 with latest (change based on event_pool and element_pool)

    exit()


## initialize evolution

evo = EvolutionaryAlgorithm(element_pool, event_pool, events_per_frame).initialize_population(100)

## run evolution

try:
    evo.run(1000, patience= 200)
except KeyboardInterrupt:
    print('evolution stopped by user request')

## evaluate results

print('========================================================================')
print('========================================================================')

winner = evo.get_winner()
winner.compute_fitness(events_per_frame) #, log= True) # log= True to show fitness computation on winner
print('winner:\n')
print(winner)
print(f'best_fitness: {winner.fitness}\n')
