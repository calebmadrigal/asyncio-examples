import asyncio

@asyncio.coroutine
def waitn(n):
    asyncio.sleep(n)
    return "I waited {}".format(n)

@asyncio.coroutine
def run_parallel():
    # Results will be in order called
    results = yield from asyncio.gather(waitn(3), waitn(1), waitn(2))
    print("Results: {}".format(results))

@asyncio.coroutine
def run_parallel2():
    tasks = [waitn(i) for i in (3,1,2)]
    # Results will be in order called
    results = yield from asyncio.gather(*tasks)
    print("Results2: {}".format(results))

@asyncio.coroutine
def run_parallel3():
    tasks = [asyncio.async(waitn(i)) for i in (3,1,2)]
    done, pending = yield from asyncio.wait(tasks)
    # Results will NOT necessarily be in the order called
    results = [future.result() for future in done]
    print("Results3: {}".format(results))

loop = asyncio.get_event_loop()
loop.run_until_complete(run_parallel())
loop.run_until_complete(run_parallel2())
loop.run_until_complete(run_parallel3())
loop.close()
