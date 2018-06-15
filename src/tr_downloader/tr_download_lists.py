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
import os
from datetime import date, timedelta, datetime
from typing import Generator, Optional

from aiohttp import ClientSession

from .utils import as_completed_limited, download, ensure_dir

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
    return the_date.strftime(DATE_FORMAT)


def date_to_url(the_date: date, base_url: str) -> str:
    return base_url + the_date.strftime(DATE_FORMAT_URL)


def make_downloader(url_prefix: str, save_path: str, session, query_params):
    async def f(file_obj):
        ensure_dir(save_path)
        print(save_path)
        for line in file_obj:
            filename = line.strip()
            await download(url_prefix + '/' + filename,
                           os.path.join(save_path, filename),
                           session,
                           query_params)

    return f


async def run(begin: Optional[date],
              end: Optional[date],
              save_path: str,
              query_params: dict,
              limit: int = 4):
    async with ClientSession() as session:
        token = query_params['t']

        info = None

        async with session.get('http://127.0.0.1:3006/requests/1effae5cc10f4aeda5383cddda17d219') as resp:
            info = await resp.json()

        d1 = datetime.strptime(info['time_start'][:10], DATE_FORMAT_URL).date() if begin is None else begin
        d2 = datetime.strptime(info['time_end'][:10], DATE_FORMAT_URL).date() if end is None else end

        urls_and_paths = ((date_to_url(d, SERVER_HOST + '/data/test/'),
                           os.path.join(save_path, date_to_fn(d)))
                          for d in gen_dates(d1, d2))

        coros = (download(url,
                          date_path + '.txt',
                          session,
                          query_params=query_params,
                          callback=make_downloader(url, date_path, session, query_params)
                          )
                 for url, date_path in urls_and_paths)

        for i in as_completed_limited(coros, limit):
            await i


def main_func():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-t', '--token', required=True)
    parser.add_argument('-d', '--dir', default='./data_downloads')
    parser.add_argument('-b', '--begin')
    parser.add_argument('-e', '--end')

    args = parser.parse_args()

    d1 = None if args.begin is None else datetime.strptime(args.begin, DATE_FORMAT_URL).date()
    d2 = None if args.end is None else datetime.strptime(args.end, DATE_FORMAT_URL).date()

    save_path = args.dir
    ensure_dir(save_path)

    parameters = {'t': args.token}

    loop = asyncio.get_event_loop()
    # https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.AbstractEventLoop.run_until_complete
    loop.run_until_complete(run(d1, d2, save_path, query_params=parameters))
    loop.close()

    return 0
