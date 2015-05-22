import asyncio
import time
from urllib.request import urlopen

@asyncio.coroutine
def count_to_10():
    for i in range(11):
        print("Counter: {}".format(i))
        yield from asyncio.sleep(.5)

def get_page_len(url):
    # This is the blocking sleep (not the async-friendly one)
    time.sleep(2)
    page = urlopen(url).read()
    return len(page)

@asyncio.coroutine
def run_get_page_len():
   loop = asyncio.get_event_loop()

   future1 = loop.run_in_executor(None, get_page_len, 'http://calebmadrigal.com')

   #data1 = yield from future1
   return future1

@asyncio.coroutine
def print_data_size():
   data = yield from run_get_page_len()
   print("Data size: {}".format(data))


loop = asyncio.get_event_loop()
tasks = [
    asyncio.async(count_to_10()),
    asyncio.async(print_data_size())]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()

