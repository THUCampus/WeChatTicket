# -*- coding: utf-8 -*-
#
import datetime
import hashlib
import json
import logging
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from WeChatTicket.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET

from django.http import Http404, HttpResponse
from django.template.loader import get_template
from django.db import transaction
from WeChatTicket import settings
from codex.baseview import BaseView
from wechat.models import User,Activity,Ticket


__author__ = "Epsirom"


class WeChatHandler(object):

    logger = logging.getLogger('WeChat')

    def __init__(self, view, msg, user):
        """
        :type view: WeChatView
        :type msg: dict
        :type user: User or None
        """
        self.input = msg
        self.user = user
        self.view = view

    def book_ticket(self,act_id):
        acts = Activity.objects.select_for_update().filter(id=int(act_id))
        with transaction.atomic():
            act = acts[0]      
            if act.remain_tickets > 0:
                act.remain_tickets -= 1
                act.save()
            else:
                return ''
        #not return: there's tickets left!
        return self.create_ticket(act_id)

    def create_ticket(self,id):
        currentTime = datetime.datetime.now().timestamp()
        unique_id = uuid.uuid5(uuid.NAMESPACE_DNS,self.user.student_id + id + str(currentTime))
        activity = Activity.objects.get(id = int(id))
        Ticket.objects.create(student_id = self.user.student_id, unique_id = unique_id,
        activity = activity, status = Ticket.STATUS_VALID)
        return self.url_ticket(unique_id)

    def get_ticket_by_act(self,id):
        activity = self.get_activity(id)
        ticket = Ticket.objects.filter(student_id = self.user.student_id, activity = activity,status = Ticket.STATUS_VALID)
        if ticket:
            return True
        else:
            return False


    def check(self):
        raise NotImplementedError('You should implement check() in sub-class of WeChatHandler')

    def handle(self):
        raise NotImplementedError('You should implement handle() in sub-class of WeChatHandler')

    def get_context(self, **extras):
        return dict(
            FromUserName=self.input['ToUserName'],
            ToUserName=self.input['FromUserName'],
            **extras
        )

    def reply_text(self, content):
        return get_template('text.xml').render(self.get_context(
            Content=content
        ))

    def reply_news(self, articles):
        if len(articles) > 8:
            self.logger.warn('Reply with %d articles, keep only 8', len(articles))
        return get_template('news.xml').render(self.get_context(
            Articles=articles[:8]
        ))

    def reply_single_news(self, article):
        return self.reply_news([article])

    def get_message(self, name, **data):
        if name.endswith('.html'):
            name = name[: -5]
        return get_template('messages/' + name + '.html').render(dict(
            handler=self, user=self.user, **data
        ))
        #self.logger.warn(repr(result))
        #return result

    def get_activity(self,id):
        activity = Activity.objects.filter(id=int(id))
        if not activity:
            return activity
        return activity[0]

    def get_activities(self):
        activities = Activity.objects.filter(status = Activity.STATUS_PUBLISHED)
        return activities

    def get_tickets(self):
        ticket_list = []
        tickets = Ticket.objects.filter(student_id = self.user.student_id,status = Ticket.STATUS_VALID)
        for i in tickets:
            ticket_list.append(i)
        tickets = Ticket.objects.filter(student_id = self.user.student_id,status = Ticket.STATUS_USED)
        for i in tickets:
            ticket_list.append(i)
        tickets = Ticket.objects.filter(student_id = self.user.student_id,status = Ticket.STATUS_CANCELLED)
        for i in tickets:
            ticket_list.append(i)    
        return ticket_list

    def is_msg_type(self, check_type):
        return self.input['MsgType'] == check_type

    def is_text(self, *texts):
        return self.is_msg_type('text') and (self.input['Content'].split()[0] in texts)

    def is_event_click(self, *event_keys):
        return self.is_msg_type('event') and (self.input['Event'] == 'CLICK') and (self.input['EventKey'] in event_keys)

    def is_event(self, *events):
        return self.is_msg_type('event') and (self.input['Event'] in events)

    def is_text_command(self, *commands):
        return self.is_msg_type('text') and ((self.input['Content'].split() or [None])[0] in commands)

    def url_help(self):
        return settings.get_url('u/help')

    def url_bind(self):
        return settings.get_url('u/bind', {'openid': self.user.open_id})
    
    def url_book(self,id):
        return settings.get_url('u/activity',{'id': id})

    def url_ticket(self,ticket):
        return  settings.get_url('u/ticket',{'openid': self.user.open_id,'ticket':ticket})


class WeChatEmptyHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('The server is busy')


class WeChatError(Exception):

    def __init__(self, errcode, errmsg, *args, **kwargs):
        super(WeChatError, self).__init__(errmsg, *args, **kwargs)
        self.errcode = errcode
        self.errmsg = errmsg

    def __repr__(self):
        return '[errcode=%d] %s' % (self.errcode, self.errmsg)


class WeChatLib(object):

    logger = logging.getLogger('wechatlib')
    access_token = ''
    access_token_expire = datetime.datetime.fromtimestamp(123456789)
    token = WECHAT_TOKEN
    appid = WECHAT_APPID
    secret = WECHAT_SECRET

    def __init__(self, token, appid, secret):
        super(WeChatLib, self).__init__()
        self.token = token
        self.appid = appid
        self.secret = secret

    def check_signature(self, signature, timestamp, nonce):
        tmp_list = sorted([self.token, timestamp, nonce])
        tmpstr = hashlib.sha1(''.join(tmp_list).encode('utf-8')).hexdigest()
        return tmpstr == signature

    @classmethod
    def _http_get(cls, url):
        req = urllib.request.Request(url=url)
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        return res.decode()

    @classmethod
    def _http_post(cls, url, data):
        req = urllib.request.Request(
            url=url, data=data if isinstance(data, bytes) else data.encode()
        )
        res_data = urllib.request.urlopen(req)
        res = res_data.read()
        return res.decode()

    @classmethod
    def _http_post_dict(cls, url, data):
        return cls._http_post(url, json.dumps(data, ensure_ascii=False))

    @classmethod
    def get_wechat_access_token(cls):
        if datetime.datetime.now() >= cls.access_token_expire:
            print("appid=%s secret=%s" %(cls.appid, cls.secret))
            res = cls._http_get(
                'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (
                    cls.appid, cls.secret
                )
            )
            rjson = json.loads(res)
            if rjson.get('errcode'):
                raise WeChatError(rjson['errcode'], rjson['errmsg'])
            cls.access_token = rjson['access_token']
            cls.access_token_expire = datetime.datetime.now() + datetime.timedelta(seconds=rjson['expires_in'] - 300)
            cls.logger.info('Got access token %s', cls.access_token)
        return cls.access_token

    def get_wechat_menu(self):
        res = self._http_get(
            'https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s' % (
                self.get_wechat_access_token()
            )
        )
        rjson = json.loads(res)
        return rjson.get('menu', {}).get('button', [])

    def set_wechat_menu(self, data):
        res = self._http_post_dict(
            'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s' % (
                self.get_wechat_access_token()
            ), data
        )
        rjson = json.loads(res)
        if rjson.get('errcode'):
            raise WeChatError(rjson['errcode'], rjson['errmsg'])


class WeChatView(BaseView):

    logger = logging.getLogger('WeChat')

    lib = WeChatLib('', '', '')

    handlers = []
    error_message_handler = WeChatEmptyHandler
    default_handler = WeChatEmptyHandler

    def _check_signature(self):
        query = self.request.GET
        return self.lib.check_signature(query['signature'], query['timestamp'], query['nonce'])

    def do_dispatch(self, *args, **kwargs):
        if not settings.IGNORE_WECHAT_SIGNATURE and not self._check_signature():
            self.logger.error('Check WeChat signature failed')
            raise Http404()
        if self.request.method == 'GET':
            return HttpResponse(self.request.GET['echostr'])
        elif self.request.method == 'POST':
            return HttpResponse(self.handle_wechat_msg(), content_type='application/xml')
        else:
            return self.http_method_not_allowed()

    def handle_wechat_msg(self):
        msg = self.parse_msg_xml(ET.fromstring(self.request.body))
        if 'FromUserName' not in msg:
            return self.error_message_handler(self, msg, None).handle()
        user, created = User.objects.get_or_create(open_id=msg['FromUserName'])
        if created:
            self.logger.info('New user: %s', user.open_id)
        try:
            for handler in self.handlers:
                inst = handler(self, msg, user)
                if inst.check():
                    return inst.handle()
            return self.default_handler(self, msg, user).handle()
        except:
            self.logger.exception('Error occurred when handling WeChat message %s', msg)
            return self.error_message_handler(self, msg, user).handle()

    @classmethod
    def parse_msg_xml(cls, root_elem):
        msg = dict()
        if root_elem.tag == 'xml':
            for child in root_elem:
                msg[child.tag] = child.text
        return msg
