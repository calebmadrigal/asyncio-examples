""" Downloads a few web pages in parallel, and counts how many times a specified
word is used in each of them. """

import asyncio
import aiohttp

@asyncio.coroutine
def download_and_count_word(word, url):
    response = yield from aiohttp.request('GET', url)
    text = yield from response.read()
    return text.decode().count(word)

@asyncio.coroutine
def count_word_in_pages(word, urls):
    tasks = [download_and_count_word(word, url) for url in urls]
    counts = yield from asyncio.gather(*tasks)

    for i in range(len(urls)):
        url = urls[i]
        count = counts[i]
        print("{} appears {} times in {}".format(word, count, url))

word = "the"
pages = ["http://calebmadrigal.com",
         "http://yahoo.com",
         "http://xkcd.com",
         "http://reddit.com",
         "http://news.ycombinator.com"]

loop = asyncio.get_event_loop()
loop.run_until_complete(count_word_in_pages(word, pages))
loop.close()

