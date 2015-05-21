""" Simple mutually-recursive coroutines with asyncio. Note that these recursive calls
continue to grow the stack (and will eventually hit the maximum recursion depth 
exception if too many recursive calls are made. """

import asyncio

@asyncio.coroutine
def a(n):
    print("A: {}".format(n))
    if n > 10: return n
    else: yield from b(n+1)

@asyncio.coroutine
def b(n):
    print("B: {}".format(n))
    yield from a(n+1)

loop = asyncio.get_event_loop()
loop.run_until_complete(a(0))

