from model import BeeModel
import time
def main(steps):
    start_time = time.time()
    model = BeeModel()
    model.run(steps)
    end_time = time.time()
    print("Execution time: ", end_time - start_time)

if __name__ == "__main__":
    main(100)