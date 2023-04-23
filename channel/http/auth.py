# encoding:utf-8

import jwt
import datetime
import time
from flask import jsonify, request
from common import const
from config import channel_conf
import sys
import os
from database import admin_user

this_dir = os.path.dirname(__file__)
sys.path.append(this_dir)
sys.path.append(os.path.join(this_dir, '..'))
sys.path.append(os.path.join(this_dir, '..', 'database'))


class Auth():
    def __init__(self, login):
    # argument 'privilegeRequired' is to set up your method's privilege
    # name
        self.login = login
        super(Auth, self).__init__()

    @staticmethod
    def encode_auth_token(user_id, password, login_time):
        """
        生成认证Token
        :param user_id: int
        :param login_time: datetime
        :return: string
        """
        try:
            payload = {
                'iss': 'ken',  # 签名
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=10),  # 过期时间
                'iat': datetime.datetime.utcnow(),  # 开始时间
                'data': {
                    'id': user_id,
                    'password':password,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                channel_conf(const.HTTP).get('http_auth_secret_key'),
                algorithm='HS256'
            )  # 加密生成字符串
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            # 取消过期时间验证
            payload = jwt.decode(auth_token, channel_conf(const.HTTP).get(
                'http_auth_secret_key'), algorithms='HS256')  # options={'verify_exp': False} 加上后不验证token过期时间
            if ('data' in payload and 'id' in payload['data']):
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'


def authenticate(user_id, password):
    from database import admin_user
    """
    用户登录，登录成功返回token
    :param password:
    :return: json
    """
    
    authPassword = channel_conf(const.HTTP).get('http_auth_password')
    if (not admin_user.AdminUserDao().check(user_id,password)):
        return False
    else:
        login_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        token = Auth.encode_auth_token(user_id, password, login_time)
        return token


def identify(request):
    
    """
    用户鉴权
    :return: list
    """
    try:
        authPassword = channel_conf(const.HTTP).get('http_auth_password')
        if (not authPassword):
            return True
        if (request is None):
            return False
        authorization = request.cookies.get('Authorization')
        if (authorization):
            payload = Auth.decode_auth_token(authorization)
            if not isinstance(payload, str):
                authPassword = channel_conf(
                    const.HTTP).get('http_auth_password')
                user_id = payload['data']['id']
                password = payload['data'].get('password')
                if admin_user.AdminUserDao().check(user_id,password):
                    return True
                else:
                    return False
        return False
 
    except jwt.ExpiredSignatureError:
        #result = 'Token已更改，请重新登录获取'
        return False
 
    except jwt.InvalidTokenError:
        #result = '没有提供认证token'
        return False

def check_times(request):
    """
    用户使用次数鉴权
    :return: list
    """
    try:
        if (request is None):
            return False
        authorization = request.cookies.get('Authorization')
        if (authorization):
            payload = Auth.decode_auth_token(authorization)
            if not isinstance(payload, str):
                user_id = payload['data']['id']
                if admin_user.AdminUserDao().check_times(user_id):
                    return True
                else:
                    return False
        return False
 
    except jwt.ExpiredSignatureError:
        #result = 'Token已更改，请重新登录获取'
        return False
 
    except jwt.InvalidTokenError:
        #result = '没有提供认证token'
        return False