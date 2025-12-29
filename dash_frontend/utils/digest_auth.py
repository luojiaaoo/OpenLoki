from hashlib import md5
import uuid
import time
from configure import conf
from flask import request


class DigestAuth:
    """一个简单的Flask Digest认证工具类"""

    def __init__(self, realm=conf.app_title):
        self.realm = realm
        self.qop = 'auth'

    def generate_challenge(self, is_stale=False):
        """生成WWW-Authenticate挑战头"""
        nonce = uuid.uuid4().hex + ':' + str(int(time.time()))
        challenge = f'Digest realm="{self.realm}", qop="{self.qop}", nonce="{nonce}", algorithm=MD5'
        if is_stale:
            challenge += ', stale=true'
        return challenge

    def parse_authorization_header(self, auth_header):
        """解析客户端传来的Authorization头"""
        # 头格式：Digest username="Mufasa", realm="...", nonce="...", uri="...", response="..."...
        parts = auth_header.split(', ')
        auth_info = {}
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                # 去掉可能存在的引号
                auth_info[key.strip()] = value.strip().strip('"')
        return auth_info

    def compute_digest(self, username, password, method, uri, nonce, nc, cnonce, qop):
        """服务器端计算期望的响应摘要"""
        # HA1 = MD5(username:realm:password)
        ha1_str = f'{username}:{self.realm}:{password}'
        ha1 = md5(ha1_str.encode()).hexdigest()

        # HA2 = MD5(method:uri)
        ha2_str = f'{method}:{uri}'
        ha2 = md5(ha2_str.encode()).hexdigest()

        # Response = MD5(HA1:nonce:nc:cnonce:qop:HA2)
        response_str = f'{ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}'
        response = md5(response_str.encode()).hexdigest()
        return response

    def authenticate(self, auth_header, method, uri, get_password_func):
        """
        主认证函数
        :param auth_header: 请求中的Authorization头
        :param method: HTTP方法 (GET, POST等)
        :param uri: 请求的URI
        :param get_password_func: 一个回调函数，根据用户名返回正确的密码
        :return: 认证成功返回用户名，失败返回None
        """
        if not auth_header or not auth_header.startswith('Digest '):
            return None

        auth_info = self.parse_authorization_header(auth_header[7:])  # 去掉开头的'Digest '

        username = auth_info.get('username')
        nonce = auth_info.get('nonce')
        uri_client: str = auth_info.get('uri')
        response = auth_info.get('response')
        nc = auth_info.get('nc', '')  # 正常要校验增量的，防止重放攻击
        cnonce = auth_info.get('cnonce', '')
        qop = auth_info.get('qop', '')

        # 1. 检查URI是否匹配
        if (i := uri_client.split('?')[0].replace(uri, '')) and not i.startswith('/'):
            return None  # URI不匹配

        # 2. 检查是否过期，如果过期返回续签标志，保证重放攻击具有时效性
        timestamp = nonce.split(':')[-1]
        if int(timestamp) < int(time.time()) - 60 * 5:  # 过期时间设为5分钟
            return ...  # nonce过期

        # 3. 通过回调函数获取该用户的正确密码
        password_correct = get_password_func(username)
        if not password_correct:
            return None  # 用户不存在

        # 4. 服务器端计算期望的摘要值
        expected_response = self.compute_digest(username, password_correct, method, uri_client, nonce, nc, cnonce, qop)

        # 5. 比较计算出的摘要和客户端传来的摘要
        if response == expected_response:
            return username  # 认证成功！
        else:
            return None  # 认证失败

    @property
    def user_id(self):
        auth_header = request.headers.get('Authorization')
        return self.parse_authorization_header(auth_header[7:]).get('username')


digest_auth = DigestAuth()
