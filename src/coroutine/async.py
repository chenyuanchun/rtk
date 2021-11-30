import asyncio
import time


async def time_consuming_work(work_time):
    print(f'Waiting for work done in {work_time}s ...')
    await asyncio.sleep(work_time)
    return f'Having worked for {work_time}s'


def _callback(future):
    print(f'result: {future.result()}')


if __name__ == '__main__':
    # _task = asyncio.Task(time_consuming_work(2))
    # _task.add_done_callback(_callback)
    start = time.perf_counter()
    tasks = [asyncio.ensure_future(time_consuming_work(t)) for t in range(1, 4)]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    for task in tasks:
        print('Task ret: ', task.result())

    print(f'time elapsed: {time.perf_counter()-start}')
