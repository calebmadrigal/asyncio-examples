# This doesn't actually explicitly use a Future, but shows how to get the same
# behavior with just coroutines.

import asyncio

@asyncio.coroutine
def slow_operation():
    yield from asyncio.sleep(1)
    return 42

@asyncio.coroutine
def call_slow_operation():
    result = yield from slow_operation()
    print("The answer is: {}".format(result))

loop = asyncio.get_event_loop()
loop.run_until_complete(call_slow_operation())
loop.close()

