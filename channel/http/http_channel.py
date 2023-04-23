# encoding:utf-8

import json
from channel.http import auth
from flask import Flask, request, render_template, make_response
from datetime import timedelta
from common import const
from common import functions
from config import channel_conf
from config import channel_conf_val
from channel.channel import Channel
import config
from flask_sqlalchemy import SQLAlchemy  # 使得数据库开始连接
from database.admin_user import db
from database import admin_user  
http_app = Flask(__name__,)
# 自动重载模板文件
http_app.jinja_env.auto_reload = True
http_app.config['TEMPLATES_AUTO_RELOAD'] = True

# 设置静态文件缓存过期时间
http_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=10)
# 连接或创建数据库
http_app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///' + config.get_db_uri()
# # 动态追踪修改设置，如未设置只会提示警告
http_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(http_app)

@http_app.route("/chat", methods=['POST'])
def chat():
    if (auth.identify(request) == False):
        return {'result': '用户校验错误，请重新登录！'} 
    if not auth.check_times(request):
        return {'result': '今日已超过使用次数，请明天再试，谢谢！'} 

    data = json.loads(request.data)
    if data:
        msg = data['msg']
        if not msg:
            return
        reply_text = HttpChannel().handle(data=data)
        return {'result': reply_text}


@http_app.route("/", methods=['GET'])
def index():
    if (auth.identify(request) == False):
        return login()
    return render_template('index.html')


@http_app.route("/login", methods=['POST', 'GET'])
def login():
    response = make_response("<html></html>", 301)
    response.headers.add_header('content-type', 'text/plain')
    response.headers.add_header('location', './')
    if (auth.identify(request) == True):
        return response
    else:
        if request.method == "POST":
            token = auth.authenticate(request.form['user_id'], request.form['password'])
            if (token != False):
                response.set_cookie(key='Authorization', value=token)
                return response
        else:
            return render_template('login.html')
    response.headers.set('location', './login?err=登录失败')
    return response


class HttpChannel(Channel):
    def startup(self):
        
        http_app.run(host='0.0.0.0', port=channel_conf(const.HTTP).get('port'))
        
        
    def handle(self, data):
        context = dict()
        img_match_prefix = functions.check_prefix(
            data["msg"], channel_conf_val(const.HTTP, 'image_create_prefix'))
        if img_match_prefix:
            data["msg"] = data["msg"].split(img_match_prefix, 1)[1].strip()
            context['type'] = 'IMAGE_CREATE'
        id = data["id"]
        context['from_user_id'] = str(id)
        context['model_type'] = data.get('model_type')
        reply = super().build_reply_content(data["msg"], context)
        if img_match_prefix:
            if not isinstance(reply, list):
                return reply
            images = ""
            for url in reply:
                images += f"[!['IMAGE_CREATE']({url})]({url})\n"
            reply = images
        return reply
