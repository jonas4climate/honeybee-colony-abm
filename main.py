from model import BeeModel
import time
def main(steps):
    model = BeeModel()
    model.run(steps)

if __name__ == "__main__":
    main(100)