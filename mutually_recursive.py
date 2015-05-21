""" Simple mutually-recursive coroutines with asyncio. Using asyncio.ensure_future
instead of yield from allows the coroutine to exit and merely schedules the next
call with the event loop, allowing infinite mutual recursion. """

import asyncio

@asyncio.coroutine
def a(n):
    print("A: {}".format(n))
    asyncio.async(b(n+1)) # asyncio.ensure_future in Python 3.4.4

@asyncio.coroutine
def b(n):
    print("B: {}".format(n))
    asyncio.async(a(n+1)) # asyncio.ensure_future in Python 3.4.4

loop = asyncio.get_event_loop()
asyncio.async(a(0))
loop.run_forever()

