import asyncio

# Tail-recursive factorial using asyncio event loop as a trampoline to
# keep the stack from growing.
@asyncio.coroutine
def factorial(n, callback, acc=1):
    if n == 0:
        callback(acc)
    else:
        asyncio.async(factorial(n-1, callback, acc*n)) # async -> ensure_future in Python 3.4.4

def done_callback(result):
    print("Result: {}".format(result))
    loop = asyncio.get_event_loop()
    loop.stop()


loop = asyncio.get_event_loop()
asyncio.async(factorial(50000, done_callback))
loop.run_forever() # Blocking call interrupted by loop.stop()
loop.close()

