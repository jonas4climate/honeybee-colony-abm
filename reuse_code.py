class State(Enum):
    RESTING = "resting"  # in the hive, resting & not interested in foraging
    DANCEFLOOR = "dancefloor"  # in the hive, on the dancefloor
    READY = "ready"  # in the hive, ready to forage
    RECRUITING = "recruiting"  # in the hive, recruiting other bees to forage
    FULL_RETURN = "full_return"  # returned from foraging with resources (success)
    EMPTY_RETURN = "empty_return"  # returned from foraging without resources (no success)
    SCOUTING = "scouting"  # scouting for resources as a result of spontaneous "decision"
    FORAGING = "foraging"  # foraging for resources as a result of recruitment
    BORN = "baby"  # in the hive, just born
