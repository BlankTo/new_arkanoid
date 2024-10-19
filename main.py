import pickle

from lib.classes import Element, EventType, Event
from lib.evolution import EvolutionaryAlgorithm


# retrieve log and create pools

with open('logs/arkanoid_logs/arkanoid_log__17_10_2024_17_47_51.pkl', 'rb') as log_file:
#with open('logs/arkanoid_logs/arkanoid_log__19_10_2024_19_28_17.pkl', 'rb') as log_file:
    log = pickle.load(log_file)

events_per_frame = []
event_pool = {}
element_pool = []
event_type_id = 0

for frame in log:
    frame_id = frame['frame_id']
    if frame_id == 0:
        element_dict = {0: 0}
        for description, element in frame['elements'].items():
            new_elem = Element(element['id'], description, None)
            element_pool.append(new_elem)
            element_dict[element['id']] = new_elem

    events = []
    for event in frame['events']:
        description = event['description']
        if description not in event_pool.keys():
            event_pool[description] = EventType(event_type_id, description)
            event_type_id += 1
        events.append(Event(event_pool[description], element_dict[event['subject']]))
    
    events_per_frame.append(events)

print('\n-------------------------------------\nelement pool:\n')
print(element_pool)
print('\n-------------------------------------\nevent pool:\n')
print(list(event_pool.values()))
print('\n-------------------------------------')

#for i in range(1000):
#    print(events_per_frame[i])
#exit()

if 0:
    from lib.classes import Individual, Object, Rule, Category
    paddle = None
    ball = None
    bricks = []
    walls = []
    for i, elem in enumerate(element_pool):
        if elem.description == 'ball':
            ball = Object(666, [elem])
        if 'paddle' in elem.description:
            paddle = Object(667, [elem])
        if 'brick' in elem.description:
            bricks.append(Object(668 + i, [elem]))
        if 'wall' in elem.description:
            walls.append(Object(768 + i, [elem]))
    collision = None
    bounce = None
    disappearance = None
    for event_type in list(event_pool.values()):
        if event_type.description == 'collision': collision = event_type
        if event_type.description == 'bounce': bounce = event_type
        if event_type.description == 'disappearance': disappearance = event_type
    ball_rule = Rule(666, collision, bounce)
    bricks_rule = Rule(667, collision, disappearance)
    ball_cat = Category(666, [ball], [ball_rule])
    bricks_cat = Category(667, bricks, [bricks_rule])
    others_cat = Category(668, [paddle] + walls, [])
    my_cat = Individual(element_pool, list(event_pool.values())).set_all([paddle, ball] + bricks + walls, [ball_rule, bricks_rule], [ball_cat, bricks_cat, others_cat])
    print('my_cat:')
    print(my_cat)
    my_cat.compute_fitness(events_per_frame, log= True)
    print(f'my_cat_fitness: {my_cat.fitness}')

    exit()


# initialize evolution

evo = EvolutionaryAlgorithm(element_pool, events_per_frame, list(event_pool.values()))

# run evolution

try:
    evo.run(1000, 100, patience= 100)
except KeyboardInterrupt:
    print('evolution stopped by user request')

# evaluate results

print('========================================================================')
print('========================================================================')

winner = evo.get_winner()
winner.compute_fitness(events_per_frame) #, log= True)
print('winner:\n')
print(winner)
print(f'best_fitness: {winner.fitness}\n')