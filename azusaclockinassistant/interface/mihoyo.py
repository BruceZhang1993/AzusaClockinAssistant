import hashlib
import os
import random
import string
import time
import uuid

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
            'User-Agent': f'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                          f'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/2.35.2',
        })
        super(Mihoyo, self).__init__()

    @staticmethod
    def _get_web_ds():
        n = 'N50pqm7FSy2AkFz2B3TqtuZMJ5TOl3Ep'
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        md5 = hashlib.md5()
        md5.update(("salt=" + n + "&t=" + i + "&r=" + r).encode())
        c = md5.hexdigest()
        return f"{i},{r},{c}"

    # @clockin_method
    async def genshiin_clockin(self):
        """原神签到"""
        if self.cookie == '':
            return False, '未配置 Cookie'
        async with self.client.get(f'{self.WEBAPI}/event/bbs_sign_reward/home?act_id={self.GENSHIIN_ACT_ID}') as resp:
            data = await resp.json()
            print(data)
            return True, 'OK'
