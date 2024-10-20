# Arkanoid

This project implements an evolutionary algorithm designed to discover patterns and rules for predicting future events based on small data. The elements and the events are taken from a simple implementation of the game Arkanoid, also included in the project, that record a log while playing.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)


## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/BlankTo/new_arkanoid
   cd new_arkanoid
   ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```


## Usage

1. Run arkanoid.py and complete a run (Optional)

    ```bash
    python arkanoid.py
    ```
    (check for save_log to be True in arkanoid.py)

    Commands:
    - left_arrow to go left
    - right_arrow to go right
    - q to Quit


2. Run main.py

    ```bash
    python main.py
    ```

## Future plans

Roadmap:
- Event with multiple subjects
- Rule with subjects and object
- time window for trigger and effect
- Add more events in the game

To Investigate:
- individual lifespan (reset by surviving)
- Define when two elements belong to the same object using events or elements' properties
- add states as elements' properties, rules update them over frames
- Automatic creation of events using parametric rules over elements properties
- element recognition

## Contacts
Created by Giorgio Mongardi.

[gio.mongardi@hotmail.it](mailto:gio.mongardi@hotmail.it)

[s292490@studenti.polito.it](mailto:s292490@studenti.polito.it)
