import asyncio
import time
import random
import urllib.request

RAND_VARIATION = 5
URL = 'http://xkcd.com'


# Blocking HTTP GET
def download_url(url):
    return urllib.request.urlopen(url).read()


@asyncio.coroutine
def worker_loop(hostid, interval):
    count = 0
    while True:
        count += 1
        print("Agent {} - loop count: {}".format(hostid, count))

        # Call download_url in the thread pool.
        loop = asyncio.get_event_loop()
        fut = loop.run_in_executor(None, download_url, URL)
        result = yield from fut
        print("Agent {} Got data len: {}".format(hostid, len(result)))

        yield from asyncio.sleep(interval + random.randint(0, RAND_VARIATION))


@asyncio.coroutine
def run_agents():
    num_agents = 5
    interval = 10
    all_agents = [worker_loop(i, interval) for i in range(1, num_agents+1)]
    yield from asyncio.gather(*all_agents)
    

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_agents())
    loop.close()

if __name__ == '__main__':
    main()

