
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def process_doo(i):
    print(i)
def worker():
    for i in range(5):
        result = process_doo(i);

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(worker) for _ in range(5)]

    # Wait for all tasks to complete
    for future in futures:
        result = future.result()



