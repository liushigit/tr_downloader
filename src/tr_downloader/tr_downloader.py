#!/usr/bin/env python3

# https://docs.python.org/3/library/typing.html
# https://docs.python.org/3/library/types.html
# https://docs.python.org/3.6/library/string.html
# https://docs.python.org/3/library/string.html
# https://stackoverflow.com/questions/42531143/type-hinting-generator-in-python-3-6
# search "async function type hint"
# https://stackoverflow.com/questions/46363945/what-does-async-await-do
# https://www.python.org/dev/peps/pep-0492/
# https://www.python.org/dev/peps/pep-0525/#asynchronous-generator-object
# https://stackoverflow.com/questions/12382719/python-way-of-printing-with-format-or-percent-form

import asyncio
import argparse
import itertools
from typing import Generator, Coroutine, Iterator, Awaitable, Any
from types import CoroutineType

from datetime import date, timedelta, datetime
from aiohttp import ClientSession

from time import sleep

DATE_FORMAT = '%Y%m%d'
DATE_FORMAT_URL = '%Y-%m-%d'
CHUNK_SIZE = 64

SERVER_HOST = 'http://127.0.0.1:3006'


# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress_bar(iteration, total, prefix='', suffix='', width=20, fill='█'):
    filled_length = int(width * iteration // total)
    bar = fill * filled_length + '-' * (width - filled_length)
    percent = iteration / float(total) * 100
    print(f"\r{prefix} |{bar}| {percent:.1f}% {suffix}", end='\r')
    # print("\r{} completed".format(percent), end='\r')
    if iteration >= total:
        print()


def gen_dates(begin: date, end: date) -> Generator[date, None, None]:
    delta = end - begin
    days = delta.days + 1

    for i in range(days):
        yield begin + timedelta(days=i)


def date_to_fn(the_date: date) -> str:
    return the_date.strftime(DATE_FORMAT) + '.txt'


def date_to_url(the_date: date, base_url: str) -> str:
    return base_url + the_date.strftime(DATE_FORMAT_URL)


# http://aiohttp.readthedocs.io/en/stable/client.html
async def download(url: str,
                   file_path: str,
                   session: ClientSession,
                   params: dict,
                   chunk_size: int = 1
                   ):
    async with session.get(url, params=params) as resp:
        if resp.status > 200:
            # print("{:s} : {:d}".format(url, resp.status))
            return
        elif resp.status == 200:
            # print("{} downloaded".format(file_path))
            pass

        file_length = int(resp.headers.get('content-length'))

        with open(file_path, 'wb') as f:
            read = 0
            while True:
                sleep(0.1)
                chunk = await resp.content.read(chunk_size)
                read += chunk_size

                if not chunk:
                    break
                # print(read, file_length)
                print_progress_bar(read, file_length)
                f.write(chunk)


def as_completed_limited(coros: Iterator[Awaitable[Any]], limit: int):
    futures = [asyncio.ensure_future(c)
               for c in itertools.islice(coros, 0, limit)]

    async def go_through():
        while True:
            await asyncio.sleep(0)
            for f in futures:
                if f.done():
                    futures.remove(f)
                    try:
                        nf = next(coros)
                        futures.append(asyncio.ensure_future(nf))
                    except StopIteration as e:
                        pass
                    return f.result()

    while futures:
        yield go_through()


async def run(begin: date, end: date, params: dict, limit: int = 4):
    async with ClientSession() as session:
        coros = (download(date_to_url(d, '/data/test/'),
                          date_to_fn(d),
                          session,
                          params=params)
                 for d in gen_dates(begin, end))

        for i in as_completed_limited(coros, limit):
            await i


def main_func():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-t', '--token', required=True)  # TODO: required
    parser.add_argument('-d', '--dir', default='.')
    parser.add_argument('-b', '--begin')
    parser.add_argument('-e', '--end')

    args = parser.parse_args()

    d1 = datetime.strptime(args.begin, DATE_FORMAT_URL).date()
    d2 = datetime.strptime(args.end, DATE_FORMAT_URL).date()

    parameters = {'t': args.token}

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(d1, d2, params=parameters))
    loop.close()

    return 0
