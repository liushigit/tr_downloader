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

import argparse
import asyncio
from datetime import date, timedelta, datetime
from typing import Generator

from aiohttp import ClientSession

from .utils import as_completed_limited, download

DATE_FORMAT = '%Y%m%d'
DATE_FORMAT_URL = '%Y-%m-%d'
CHUNK_SIZE = 64

SERVER_HOST = 'http://127.0.0.1:3006'


def gen_dates(begin: date, end: date) -> Generator[date, None, None]:
    delta = end - begin
    days = delta.days + 1

    for i in range(days):
        yield begin + timedelta(days=i)


def date_to_fn(the_date: date) -> str:
    return the_date.strftime(DATE_FORMAT) + '.txt'


def date_to_url(the_date: date, base_url: str) -> str:
    return base_url + the_date.strftime(DATE_FORMAT_URL)


async def run(begin: date, end: date, params: dict, limit: int = 4):
    async with ClientSession() as session:
        coros = (download(date_to_url(d, SERVER_HOST + '/data/test/'),
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