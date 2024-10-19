import pickle

from classes import Element, EventType, Event
from evolution import EvolutionaryAlgorithm


# retrieve log and create pools

with open('logs/arkanoid_logs/arkanoid_log__17_10_2024_17_47_51.pkl', 'rb') as log_file:
    log = pickle.load(log_file)

events_per_frame = []
event_pool = {}
element_pool = []
event_type_id = 0

for frame in log:
    frame_id = frame['frame_id']
    if frame_id == 0:
        for description, element in frame['elements'].items():
            element_pool.append(Element(element['id'], description, None))

    events = []
    for event in frame['events']:
        description = event['description']
        if description not in event_pool.keys():
            event_pool[description] = EventType(event_type_id, description)
            event_type_id += 1
        events.append(Event(event_pool[description], event['subject']))
    
    events_per_frame.append(events)

print('\n-------------------------------------\nelement pool:\n')
print(element_pool)
print('\n-------------------------------------\nevent pool:\n')
print(list(event_pool.values()))
print('\n-------------------------------------')

#for i in range(1000):
#    print(events_per_frame[i])
#exit()


# initialize evolution

evo = EvolutionaryAlgorithm(element_pool, events_per_frame, list(event_pool.values()))

# run evolution

try:
    evo.run(1000, 100)
except KeyboardInterrupt:
    print('evolution stopped by user request')

# evaluate results

winner = evo.get_winner()
print(f'best_fitness: {winner.get_fitness()}')
winner.print_rules()