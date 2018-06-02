import itertools
import asyncio
import os

from aiohttp import ClientSession
from typing import Generator, Coroutine, Iterator, Awaitable, Any, Iterable


# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def print_progress_bar(iteration, total, prefix='', suffix='', width=20, fill='█'):
    filled_length = int(width * iteration // total)

    filled_length = min(width, filled_length)

    bar = fill * filled_length + '-' * (width - filled_length)

    percent = iteration / float(total) * 100
    percent = min(percent, 100)

    print(f"\r{prefix} |{bar}| {percent:5.1f}% {suffix}", end='\r')
    # print("\r{} completed".format(percent), end='\r')
    if iteration >= total:
        print()


# http://aiohttp.readthedocs.io/en/stable/client.html
async def download(url: str,
                   file_path: str,
                   session: ClientSession,
                   query_params: dict,
                   chunk_size: int = 64
                   ):
    try:
        async with session.get(url, params=query_params) as resp:
            if resp.status > 200:
                print("{:s} : {:d}".format(url, resp.status))
                return
            elif resp.status == 200:
                # print("{} downloaded".format(file_path))
                pass

            file_length = int(resp.headers.get('content-length'))
            # print(file_length)

            with open(file_path, 'wb') as f:
                read = 0
                while True:
                    # sleep(0.1)
                    chunk = await resp.content.read(chunk_size)
                    read += chunk_size

                    if not chunk:
                        break

                    print_progress_bar(read, file_length)

                    f.write(chunk)
    except Exception as e:
        print(e)


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


def ensure_dir(path):
    p = os.path.expanduser(path)

    if not os.path.isabs(p):
        p = os.path.abspath(p)

    if os.path.isdir(p):
        return p

    os.makedirs(p)
    return p
