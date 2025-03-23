# app/utils/decorators.py

import time
import functools

def measure_time(func):
    @functools.wraps(func)
    def wrapper_measure_time(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Tempo de execução de {func.__name__}: {execution_time:.6f} segundos")
        return result
    return wrapper_measure_time

