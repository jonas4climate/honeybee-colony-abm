# from set_parameters import BABYTIME, BABYBITE
from set_parameters import CONSUME_RATE, BABY_AGELIMIT, BABY_FEED
from Resource import Resource
def step_baby(bee):
    """
    Stays in the hive until it grows
    """
    hive = bee.hive

    if hive.food >= BABY_FEED:
        hive.food -= BABY_FEED

    if bee.age > BABY_AGELIMIT:
        bee.state = "resting"
        bee.resting_duration = 5 # Reset resting duration


def step_resting(bee):
    """
    Stay in hive and eat food
    """
    assert bee.in_hive, "Bee not in Hive."

    hive = bee.hive

    if bee.resting_duration == 0:
        bee.state = "foraging"
    elif hive.food >= CONSUME_RATE:
        bee.resting_duration -= 1  # substract one step from the resting duration
        hive.food -= CONSUME_RATE

def step_foraging(bee):
    """
    Find food and bring it back to the hive. If no food is found, look around for food
    """
    if bee.is_carrying_food:
        bee.go_to_hive()
    # else: TODO: Random walk towards resource and pathfinder back to hive

def step_dancing(bee):
    pass    #TODO: Rule for implementing dancing


BEE_STATES = {
    'baby': step_baby,
    'resting': step_resting,
    'foraging': step_foraging,
    # 'dancing': step_dance
}
