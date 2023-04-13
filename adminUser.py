# encoding:utf-8

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
sys.path.append(r"D:\Users\pengzuo\vsCode\bot-on-anything")
sys.path.append(r"D:\Users\pengzuo\vsCode\bot-on-anything\database\model")
import config
import uuid
import flask,json
from flask import request,Response,make_response
import adminUser
server=flask.Flask("user")

class AdminUser():
    __tablename__ = "tb_admin_user"
    # 表结构
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(64), nullable=True) 
    code = Column(String(64), nullable=True) 
    pwd = Column(String(64), nullable=True) 
    type = Column(Integer, nullable=True) 
    create_time = Column(String(64), nullable=True)

class AdminUserDao():
    def exists(code):
        user = config.get_db_conn().query(AdminUser).filter(AdminUser.code == code)
        if user:
            return True

    def insert():
        config.get_db_conn().add_all([AdminUser(code =str(uuid.uuid1()).replace("-", ""))])
        return 'success'

@server.route('/index',methods=['get'])#第一个参数就是路径,第二个参数支持的请求方式，不写的话默认是get
def index():
    adminUserDao = AdminUserDao()
    adminUserDao.insert()
if __name__ == '__main__':

    server.run(port=8081,debug=True,host='0.0.0.0')
