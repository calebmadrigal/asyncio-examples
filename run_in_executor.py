import asyncio
from urllib.request import urlopen

@asyncio.coroutine
def print_data_size():
   data = yield from get_data_size()
   print("Data size: {}".format(data))

# Note that this is a synchronous function
def sync_get_url(url):
   return urlopen(url).read()

@asyncio.coroutine
def get_data_size():
   loop = asyncio.get_event_loop()

   # These each run in their own thread (in parallel)
   future1 = loop.run_in_executor(None, sync_get_url, 'http://xkcd.com')
   future2 = loop.run_in_executor(None, sync_get_url, 'http://google.com')

   # While the synchronous code above is running in other threads, the event loop
   # can go do other things.
   data1 = yield from future1
   data2 = yield from future2
   return len(data1) + len(data2)

loop = asyncio.get_event_loop()
loop.run_until_complete(print_data_size())

