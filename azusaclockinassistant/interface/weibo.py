import os
import time

import click

from azusaclockinassistant.common.base import BaseInterface
from azusaclockinassistant.common.decorators import clockin_method


class Weibo(BaseInterface):
    """新浪微博"""
    def __init__(self):
        self.cookie = os.environ.get('WEIBO_COOKIE', '')
        self.super_indexes = os.environ.get('WEIBO_SUPER_INDEX', '').split(',')
        self.headers.update({
            'Cookie': self.cookie,
            'Referer': 'https://weibo.com',
            'client-version': 'v2.34.91',
            'server-version': 'v2022.08.26.2',
        })
        super(Weibo, self).__init__()

    @clockin_method
    async def super_index_sign(self):
        """微博超话签到"""
        if self.cookie == '':
            return False, '未配置 Cookie'
        for id_ in self.super_indexes:
            if id_ == '':
                continue
            ok, msg = await self._super_index_clockin(id_)
            if not ok:
                click.echo(f'超话 {id_} 签到失败：{msg}')
            else:
                click.echo(f'超话 {id_} 签到成功')
        return True, '执行完成'

    async def _super_index_clockin(self, id_):
        async with self.client.get('https://weibo.com/p/aj/general/button', params={
            'ajwvr': '6',
            'api': 'http://i.huati.weibo.com/aj/super/checkin',
            'texta': '签到',
            'textb': '已签到',
            'status': '0',
            'id': id_,
            'location': 'page_100808_super_index',
            'timezone': 'GMT+0800',
            'lang': 'zh-cn',
            'plat': 'Win32',
            'ua': self.BROWSER_UA,
            'screen': '1920*1080',
            '__rnd': str(int(round(time.time() * 1000))),
        }, headers={
            'Referer': f'https://weibo.com/p/{id_}/super_index',
            'x-requested-with': 'XMLHttpRequest',
        }) as resp:
            if 'json' not in resp.content_type:
                return False, '响应格式非JSON'
            data = await resp.json()
            return data.get('code') == '100000', data.get('msg')
