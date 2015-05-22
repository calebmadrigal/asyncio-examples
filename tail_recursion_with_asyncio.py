import asyncio

# Tail-recursive factorial using asyncio event loop as a trampoline to
# keep the stack from growing.
@asyncio.coroutine
def factorial(n, acc=1):
    if n == 0:
        print(acc)
        loop = asyncio.get_event_loop()
        loop.stop()
    else:
        asyncio.async(factorial(n-1, acc*n)) # async -> ensure_future in Python 3.4.4

loop = asyncio.get_event_loop()
asyncio.async(factorial(1000))
loop.run_forever() # Blocking call interrupted by loop.stop()
loop.close()

