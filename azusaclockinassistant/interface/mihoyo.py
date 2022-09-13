import asyncio
import hashlib
import os
import random
import string
import time
import uuid

import click

from azusaclockinassistant.common.base import BaseInterface
from azusaclockinassistant.common.decorators import clockin_method


class Mihoyo(BaseInterface):
    """米哈游"""
    WEBAPI = 'https://api-takumi.mihoyo.com'
    GENSHIIN_ACT_ID = 'e202009291139501'

    def __init__(self):
        self.cookie = os.environ.get('MIHOYO_COOKIE', '')
        self.headers.update({
            'DS': self._get_web_ds(),
            'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html',
            'Cookie': self.cookie,
            'x-rpc-device_id': str(uuid.uuid3(uuid.NAMESPACE_URL, self.cookie)),
            'User-Agent': f'Mozilla/5.0 (Linux; Android 12; PGKM10) AppleWebKit/537.36 (KHTML, like Gecko) '
                          f'Chrome/104.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.36.1',
        })
        super(Mihoyo, self).__init__()

    @staticmethod
    def _get_web_ds():
        n = 'YVEIkzDFNHLeKXLxzqCA9TzxCpWwbIbk'
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        md5 = hashlib.md5()
        md5.update(("salt=" + n + "&t=" + i + "&r=" + r).encode())
        c = md5.hexdigest()
        return f"{i},{r},{c}"

    async def _get_genshiin_accounts(self):
        async with self.client.get(f'{self.WEBAPI}/binding/api/getUserGameRolesByCookie', params={
            'game_biz': 'hk4e_cn',
        }) as resp:
            data = await resp.json()
            if data.get('retcode') != 0:
                return []
            return [(account.get('region'), account.get('game_uid'), account.get('nickname'))
                    for account in data.get('data', {}).get('list', [])]

    async def _sign_in(self, region, uid, name, tries=1):
        click.echo(f'正在尝试签到账号 {name} 第{tries}次尝试...')
        async with self.client.post(f'{self.WEBAPI}/event/bbs_sign_reward/sign', json={
            'act_id': self.GENSHIIN_ACT_ID,
            'region': region,
            'uid': uid,
        }) as resp:
            data = await resp.json()
            print(data)
            if data.get('retcode') == 0 and data.get('data', {}).get('success') == 1 \
                    and tries <= 4:
                await asyncio.sleep(random.randint(4, 10))
                await self._sign_in(region, uid, name, tries + 1)
            elif data.get('retcode') != 0 and tries <= 4:
                await asyncio.sleep(random.randint(4, 10))
                await self._sign_in(region, uid, name, tries + 1)

    @clockin_method
    async def genshiin_clockin(self):
        """原神签到"""
        if self.cookie == '':
            return False, '未配置 Cookie'
        for region, uid, name in await self._get_genshiin_accounts():
            async with self.client.get(f'{self.WEBAPI}/event/bbs_sign_reward/info', params={
                'act_id': self.GENSHIIN_ACT_ID,
                'region': region,
                'uid': uid,
            }) as resp:
                data = await resp.json()
                if data.get('retcode') != 0:
                    continue
                if data.get('data', {}).get('first_bind'):
                    click.echo(f'旅行者 {name} 是第一次绑定米游社，请先手动签到一次')
                    continue
                is_sign = '未签到' if data.get('data', {}).get('is_sign') is False else '已签到'
                click.echo(f'查询到旅行者 {name} {is_sign}...')
                if is_sign == '未签到':
                    await asyncio.sleep(random.randint(2, 8))
                    await self._sign_in(region, uid, name)
        return True, '执行结束'
