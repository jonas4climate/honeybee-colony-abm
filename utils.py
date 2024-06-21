"""
Collection of utility functions for the project.
"""

import time


def timed(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print("Execution time: ", end_time - start_time)
        return result
    return wrapper