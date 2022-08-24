import os

import click

from azusaclockinassistant.common.base import BaseInterface
from azusaclockinassistant.common.decorators import clockin_method


class Bilibili(BaseInterface):
    """哔哩哔哩"""

    GIFT_TYPE_MAP = {
        1: 'B币券',
        2: '会员购优惠券',
        3: '漫画福利券',
        4: '会员购运费券',
    }

    def __init__(self):
        self.cookie = os.environ.get('BILIBILI_COOKIE', '')
        self.headers.update({'Cookie': self.cookie})
        super(Bilibili, self).__init__()

    def _get_bilijct(self):
        for cookie_line in self.cookie.split(';'):
            key, value = cookie_line.split('=')
            if key.strip() == 'bili_jct':
                return value.strip()
        return ''

    @clockin_method
    async def live_clockin(self):
        """直播用户签到"""
        if self.cookie == '':
            return False, '未配置 Cookie'
        async with self.client.get('https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign') as resp:
            data = await resp.json()
            return data.get('code') == 0, data.get('message')

    @clockin_method
    async def manga_clockin(self):
        """漫画区签到"""
        if self.cookie == '':
            return False, '未配置 Cookie'
        async with self.client.post('https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn', data={
            'platform': 'android',
        }) as resp:
            data = await resp.json()
            return data.get('code') == 0, data.get('msg')

    @clockin_method
    async def vip_gifts(self):
        """大会员兑换福利"""
        if self.cookie == '':
            return False, '未配置 Cookie'
        async with self.client.get('https://api.bilibili.com/x/vip/privilege/my') as resp:
            data = await resp.json()
            if data.get('code') != 0:
                return False, data.get('message')
            for item in data.get('data', {}).get('list', []):
                typename = self.GIFT_TYPE_MAP.get(item.get('type'), '未知优惠券 ' + str(item.get('type')))
                if item.get('state') == 1:
                    click.echo(f'{typename} 已兑换过，跳过当前优惠')
                    continue
                ok, msg = await self._receive_gift(item.get('type'))
                if not ok:
                    click.echo(f'{typename} 兑换失败：{msg}')
                else:
                    click.echo(f'{typename} 兑换成功')
            return True, data.get('message')

    async def _receive_gift(self, type_):
        async with self.client.post('https://api.bilibili.com/x/vip/privilege/receive', data={
            'type': type_,
            'csrf': self._get_bilijct(),
        }) as resp:
            data = await resp.json()
            return data.get('code') == 0, data.get('message')
