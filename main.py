import pickle

from classes import Element, EventType, Recorded_Event
from evolution import EvolutionaryAlgorithm


# retrieve log and create pools

with open('logs/log__11_10_2024_01_12_57.pkl', 'rb') as log_file:
    log = pickle.load(log_file)

events_per_frame = []
event_pool = {}
elements = []

for frame in log:
    frame_id = frame['frame_id']
    if frame_id == 0:
        for description, element in frame['elements'].items():
            elements.append(Element(element['id'], description, None))

    events = []
    for description, event in frame['events'].items():
        if description not in event_pool.keys():
            event_pool[description] = EventType(description)
        events.append(Recorded_Event(event_pool[description], event['subject']))
    
    events_per_frame.append(events)

print('\n-------------------------------------\nelement pool:\n')
print(elements)
print('\n-------------------------------------\nevent pool:\n')
print(list(event_pool.values()))
print('\n-------------------------------------')


# initialize evolution

evo = EvolutionaryAlgorithm(elements, events_per_frame, list(event_pool.values()))

# run evolution

evo.run(100, 1000)

# evaluate results

winner = evo.get_winner()
print(winner.get_fitness())
winner.print_rules()