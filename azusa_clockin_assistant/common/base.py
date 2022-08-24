import asyncio

import aiohttp


class BaseInterface:
    BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/104.0.0.0 Safari/537.36'

    headers = {'User-Agent': BROWSER_UA}

    def __init__(self):
        self.client = aiohttp.ClientSession(headers=self.headers)

    def __del__(self):
        if self.client is not None:
            asyncio.ensure_future(self.client.close())
