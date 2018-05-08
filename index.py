# -*- coding: utf-8 -*-
# @Time    : 2018/4/15 下午10:06
# @Author  : zeali
# @Email   : zealiemai@gmail.com

import string
import random
import uuid
import json
import requests
import time
import logging
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.ERROR)


class MindReader():

    def __init__(self):
        self.ai_user = ''
        self.sender_id = str(uuid.uuid4())
        self.cookieid = ''
        self.ai_session_id = ''
        # self.init_client()

    def generate_headers(self):
        data = {
            "Content-Type": "application/json",
            "Host": "webapps.msxiaobing.com",
            "Accept-Language": "'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0",
            "Referer": "http://webapps.msxiaobing.com/MindReader",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": str(
                'cpid=' + self.cpid + '; ' +
                'salt=' + self.salt + '; ' +
                'ARRAffinity=' + self.ARRAffinity + ';' +
                'ai_user=' + self.ai_user + ';' +
                'cookieid=' + self.cookieid + ';' +
                'ai_session_id=' + self.ai_session_id
            )
        }
        return data

    def generate_post_data(self, text_key=0):

        text_map = (
            (0, u'玩'),
            (1, u'开始'),
            (2, u'是'),
            (3, u'否'),
            (4, u'不知道'),
        )
        data = {"SenderId": self.sender_id, "Content": {"Text": dict(text_map)[text_key], "Image": ""}}
        if text_key == 0:
            data['Content']['Metadata'] = {"Q20H5Enter": "true"}
        logging.info('post_data:' + str(data))
        return data

    def generate_id(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
                       for _ in range(5)
                       )

    def generate_ai_user(self):
        ai_user_id = self.generate_id()
        year = str(time.strftime("%Y"))
        month = str(int(time.strftime("%m")))
        day = str(int(time.strftime("%d")))

        expires_time = year + "-" + month + "-" + day + str(time.strftime("T%H:%M:%S.")) + \
                       str(int(str(datetime.utcnow().microsecond)[3:6]) / 1e3)[2:5] + \
                       u'Z'

        self.ai_user = ai_user_id + '|' + expires_time

    def generate_ai_session(self):
        """生成session"""
        nowTime = str(int(time.time() * 1000))
        ai_session_id = self.generate_id()
        self.ai_session_id = ai_session_id + '|' + nowTime + '|' + nowTime
        logging.info('ai_session_id:' + self.ai_session_id)

    def get_cookieid(self):
        url = 'http://webapps.msxiaobing.com/simplechat/getresponse?workflow=Q20'
        res = requests.post(url=url, headers=self.generate_headers(), json=self.generate_post_data())
        self.cookieid = res.cookies.get(name='cookieid')
        self.dialogue_parser(res._content)

    def get_wechat_authorize(self):
        url = 'http://webapps.msxiaobing.com/api/wechatAuthorize/signature?url=http://webapps.msxiaobing.com/MindReader'
        res = requests.get(url=url, headers=self.generate_headers())
        logging.info('wechat_authorize:' + res.text)

    def init_client(self):
        url = 'http://webapps.msxiaobing.com/MindReader'
        res = requests.get(url)
        self.cpid = res.cookies.get(name='cpid')
        self.salt = res.cookies.get(name='salt')
        self.ARRAffinity = res.cookies.get(name='ARRAffinity')
        self.get_wechat_authorize()
        self.get_cookieid()
        self.generate_ai_session()
        self.generate_ai_user()


    def dialogue_parser(self, return_data):
        soup = BeautifulSoup(return_data, "html.parser")
        json_content = json.loads(soup.find(id='xb_responses')['data-json'])
        data = ''
        logging.debug('return_json:' + str(json_content))
        for i in range(len(json_content)):
            text = json_content[i]['Content']['Text']
            data += text if text else ''
        print 'Question:' + data
        return data

    def choice(self,decision = 2):
        url = 'http://webapps.msxiaobing.com/simplechat/getresponse?workflow=Q20'
        res = requests.post(url=url, headers=self.generate_headers(), json=self.generate_post_data(decision))
        self.dialog_index = self.dialog_index + 1
        self.dialogue_parser(res._content)

    def start(self):
        self.init_client()
        url = 'http://webapps.msxiaobing.com/simplechat/getresponse?workflow=Q20'
        res = requests.post(url=url, headers=self.generate_headers(), json=self.generate_post_data(1))
        res_parser = self.dialogue_parser(res._content)

        self.dialog_index = 0
        while self.dialog_index < 17 and res_parser:
            choice_range = ['y', 'n', 'u']
            now_choice = raw_input('Input your answer for yes/no/uncertain? [y/n/u]:').lower()
            if now_choice in choice_range:
                choice_map = (
                    ('y', 2),
                    ('n', 3),
                    ('u', 4),
                )
                self.choice(dict(choice_map)[now_choice])
            else:
                print 'Please input in the range for y/n/u'



mr = MindReader()
mr.start()