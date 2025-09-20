import os
import time
import random

def long_time_task(name):
    print(f'Run task {name}(pid:{os.getpid()}) ...')
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print(f'Finish {name}(pid:{os.getpid()}) task with {(end - start):.1f} ...')

def write_func(q):
    print(f'Process {os.getpid()} to write:')
    for value in ['A', 'B', 'C']:
        print(f'Put {value} to queue ...')
        q.put(value)
        time.sleep(random.random())

def read_func(q):
    print(f'Process {os.getpid()} to read:')
    while True:
        value = q.get(True)
        print(f'Get {value} from queue')



"""
x = 5

for i in range(1, x + 1):
    a = " " * (x - i)
    b = "*" * (2 * i - 1)
    print(a + b)

"""