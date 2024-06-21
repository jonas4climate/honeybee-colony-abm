"""This module defines the different states a bee can be in. The state determines the bee's behavior."""

from Resource import Resource
from set_parameters import CONSUME_RATE, BABY_AGELIMIT, BABY_FEED


def step_baby(bee):
    """Bee babies stay in the hive until they've grown."""
    assert bee.in_hive, f"Bee '{bee}' (baby) is not in Hive."
    hive = bee.hive
    if hive.food >= BABY_FEED:
        bee.energy += BABY_FEED
        hive.food -= BABY_FEED
    if bee.age > BABY_AGELIMIT:
        bee.state = "resting"
        bee.resting_duration = 5 # Reset resting duration

def step_resting(bee):
    """Stay in hive and eat food."""
    assert bee.in_hive, "Bee not in Hive."
    hive = bee.hive
    if bee.resting_duration == 0:
        bee.state = "foraging"
    elif hive.food >= CONSUME_RATE:
        bee.resting_duration -= 1
        hive.food -= CONSUME_RATE

def step_foraging(bee):
    """Find food and bring it back to the hive. If no food is found, look around for food."""
    if bee.carrying_resource:
        bee.go_to_hive()
    else: 
        bee.random_walk()

def step_dancing(bee):
    """Dance to communicate with other bees."""
    # TODO : Rule for implementing dancing
    pass


STATES_STEP = {
    'baby': step_baby,
    'resting': step_resting,
    'foraging': step_foraging,
    'dancing': step_dancing
}