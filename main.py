import time

from BeeModel import BeeModel
from utils import timed


@timed
def main(steps):
    model = BeeModel()
    model.run(steps)


if __name__ == "__main__":
    main(100)