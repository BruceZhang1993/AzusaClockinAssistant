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
        })
        super(Weibo, self).__init__()

    @clockin_method
    async def super_index_sign(self):
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
        """微博超话签到"""
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
            'plat': 'Linux x86_64',
            'ua': self.BROWSER_UA,
            'screen': '1920*1080',
            '__rnd': str(int(round(time.time() * 1000))),
        }) as resp:
            data = await resp.json()
            print(data)
            return data.get('code') == 0, data.get('msg')
