# encoding:utf-8

from uuid import uuid4
from flask import request, Response, make_response
from flask import current_app as app
import json
import flask
from flask_sqlalchemy import SQLAlchemy  # 使得数据库开始连接
import redis

from sqlalchemy.ext.declarative import declarative_base
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
)
import sys
import os

this_dir = os.path.dirname(__file__)
sys.path.append(this_dir)
sys.path.append(os.path.join(this_dir, '..'))
sys.path.append(os.path.join(this_dir, '..', 'http'))
print(sys.path)

import logging as log
import config

redis_db = config.get_redis()

db = SQLAlchemy()

# 相当于Django model
Base = declarative_base()
REDIS_KEY = "bot.user.times."
# 普通帐户使用次数
USE_TIMES = 20
# 过期时间(秒)
EXPIRE_TIME = 60*60*12

class AdminUser(Base):
    __tablename__ = "tb_admin_user"
    # 表结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(64), nullable=True)
    code = Column(String(64), nullable=True)
    pwd = Column(String(64), nullable=True)
    type = Column(Integer, nullable=True)
    create_time = Column(String(64), nullable=True)

class AdminUserDao():
    def getByPwd(self, pwd):
        return db.session.query(AdminUser).filter(AdminUser.pwd == pwd).first()

    # 是否已经注册
    def check(self, code, pwd):
        user = db.session.query(AdminUser).filter(
            AdminUser.code == code and AdminUser.pwd == pwd).first()
        if user:
            return True
        return False

    def getByCode(self, code):
        return db.session.query(AdminUser).filter(AdminUser.code == code).first()

    # 是否还有次数
    def check_times(self, code):
        key = REDIS_KEY + code
        user = self.getByCode(code)
        if not user:            
            # 不存在用户
            return False
        log.debug('user exists, code={}.'.format(code))
        # 普通帐户一天只有n次
        if user.type == 0:
            times = redis_db.get(key)
            # 第一次使用
            if not times:
                redis_db.set(name=key, value=USE_TIMES, ex=EXPIRE_TIME)
                return True
            log.debug("user times, code={}, times={}".format(code, redis_db.get(key)))
            print("user times, code={}, times={}".format(code, redis_db.get(key)))
            if times:
                redis_db.set(key, int(times) - 1)
                if int(times) <= 0:
                    return False
        return True

    def insert(self, code):
        key = REDIS_KEY + code
        user = self.getByCode(code)
        if user:
            log.debug('user exists, code={}.'.format(code))
            return user.pwd
        user = AdminUser()
        # adminUser.code = str(uuid.uuid1()).replace("-", "")
        user.code = code
        user.pwd = short_uuid()
        user.type = 0
        db.session.add_all([user])
        db.session.commit()
        log.debug('user create success, code={}.'.format(code))
        redis_db.set(name=key, value=USE_TIMES, ex=EXPIRE_TIME)
        return user.pwd


# 第一个参数就是路径,第二个参数支持的请求方式，不写的话默认是get
# @app.route('/insert/<code>', methods=['get'])
def insert(code):
    adminUserDao = AdminUserDao()
    r = adminUserDao.insert(code)
    log.debug(r)
    return r
# @app.route('/check_times/<code>', methods=['get'])
def check_times(code):
    adminUserDao = AdminUserDao()
    return str(adminUserDao.check_times(code))

uuidChars = ("a", "b", "c", "d", "e", "f",
             "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
             "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
             "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I",
             "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
             "W", "X", "Y", "Z")


def short_uuid():
    uuid = str(uuid4()).replace('-', '')
    result = ''
    for i in range(0, 8):
        sub = uuid[i * 4: i * 4 + 4]
        x = int(sub, 16)
        result += uuidChars[x % 0x3E]
    return result


# if __name__ == '__main__':
#     try:
#         db = SQLAlchemy(app)
#         app.run(port=8081, debug=True, host='0.0.0.0')
#     except Exception as e:
#         log.error("App startup failed!")
