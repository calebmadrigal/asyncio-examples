import asyncio

@asyncio.coroutine
def slow_operation(future):
    yield from asyncio.sleep(1)
    future.set_result(42)

@asyncio.coroutine
def call_slow_operation():
    fut = asyncio.Future()
    yield from slow_operation(fut)
    result = fut.result()
    print("The answer is: {}".format(result))

loop = asyncio.get_event_loop()
loop.run_until_complete(call_slow_operation())
loop.close()

