# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import Activity, Ticket
from WeChatTicket.settings import WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET
from wechat.wrapper import WeChatLib
import threading
from datetime import datetime
import time
import random
import string



__author__ = "Epsirom"

remainTicketsLock = threading.Lock()

class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_text('抢啥') or self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)
        wechat_menu = lib.get_wechat_menu()
        if len(wechat_menu) < 2:
            return self.reply_text('暂时没有可抢票的活动')
        elif len(wechat_menu[1]['sub_button']) == 0:
            return self.reply_text('暂时没有可抢票的活动')
        else:
            acti_list = wechat_menu[1]['sub_button']
            news_list = []
            for acti in acti_list:
                try:
                    activity = Activity.objects.get(name=acti['name'])
                    news_list.append({
                        'Title': activity.name,
                        'Description': activity.description,
                        'PicUrl': activity.pic_url,
                        'Url': self.url_activity_detail(activity.id)
                    })
                except:
                    return self.reply_text('数据库内出现了重名活动，请联系管理员-_-!')

            return self.reply_news(news_list)


class BookTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('抢票') or self.is_event_click(self.view.event_keys['book_header'])

    def handle(self):
        if self.is_msg_type('event'):
            """
            lib = WeChatLib(WECHAT_TOKEN, WECHAT_APPID, WECHAT_SECRET)
            acti_list = lib.get_wechat_menu()[1]['sub_button']
            for acti in acti_list:
                if acti['key'] == self.input['EventKey']:
                    activity_name = acti['name']
                    break
            try:
                activity = Activity.objects.get(name=activity_name)
            """
            activity_id = int(self.input['EventKey'][len(self.view.event_keys['book_header']):])
            try:
                activity = Activity.objects.get(id=activity_id)
            except:
                return self.reply_text('该活动不存在')
        elif self.is_msg_type('text'):
            try:
                activity_name = self.input['Content'].split()[1]
            except:
                return self.reply_text('格式错误0_0 抢票请输入"抢票 活动名"')
            try:
                activity = Activity.objects.get(name=activity_name)
            except:
                return self.reply_text('活动名错误?_? 该活动不存在或有重名活动')

        if not self.user.student_id:
            return self.reply_text('你还没绑定学号哟')

        if len(Ticket.objects.filter(activity=activity, student_id=self.user.student_id)) > 0:
            return self.reply_text('一个人只能抢一张票哦')

        currentTime = int(time.time())
        if int(time.mktime(activity.book_start.timetuple())) > currentTime:
            return self.reply_text('抢票尚未开始')
        elif int(time.mktime(activity.book_end.timetuple())) < currentTime:
            return self.reply_text('抢票已结束')

        remainTicketsLock.acquire()
        if activity.remain_tickets <= 0:
            remainTicketsLock.release()
            return self.reply_text('来晚啦T_T 票都被抢光啦')
        else:
            activity.remain_tickets -= 1
            activity.save()
            remainTicketsLock.release()
            ticket = Ticket(
                student_id=self.user.student_id,
                unique_id=self.user.student_id + ''.join(
                    random.choice(string.digits + string.ascii_letters) for x in range(32)),
                activity=activity,
                status=Ticket.STATUS_VALID,
            )
            ticket.save()
            return self.reply_text('恭喜^_^抢票成功')


class GetTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('取票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        if not self.user.student_id:
            return self.reply_text('你还没有绑定学号')

        ticket_list = []
        news_list = []
        if self.is_msg_type('event'):
            ticket_list = list(Ticket.objects.filter(student_id=self.user.student_id))
        elif self.is_msg_type('text'):
            try:
                activity_name = self.input['Content'].split()[1]
            except:
                return self.reply_text('格式错误0_0 取票请输入"取票 活动名"')
            try:
                activity = Activity.objects.get(name=activity_name)
            except:
                return self.reply_text('活动名错误?_? 该活动不存在或有重名活动')

            ticket_list = list(Ticket.objects.filter(activity=activity, student_id=self.user.student_id))

        if len(ticket_list) == 0:
            return self.reply_text('你还没有抢到票哦')

        for ticket in ticket_list:
            news_list.append({
                'Title': '电子票：' + ticket.activity.name,
                'Description': ticket.student_id,
                'PicUrl': ticket.activity.pic_url,
                'Url': self.url_ticket_detail(self.user.open_id, ticket.unique_id)
            })

        return self.reply_news(news_list)


class CancelTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('退票')

    def handle(self):
        if not self.user.student_id:
            return self.reply_text('你还没有绑定学号哦')

        try:
            activity_name = self.input['Content'].split()[1]
        except:
            return self.reply_text('格式错误0_0 退票请输入"退票 活动名"')
        try:
            activity = Activity.objects.get(name=activity_name)
        except:
            return self.reply_text('活动名错误?_? 该活动不存在或有重名活动')

        try:
            ticket = Ticket.objects.get(activity=activity, student_id=self.user.student_id)
        except:
            return self.reply_text('你就没抢到，退啥退→_→')
        if int(time.mktime(ticket.activity.book_end.timetuple())) < int(time.time()):
            return self.reply_text('抢票结束后就不能再退了哦！')

        ticket.status = Ticket.STATUS_CANCELLED
        ticket.save()
        remainTicketsLock.acquire()
        ticket.activity.remain_tickets += 1
        ticket.activity.save()
        remainTicketsLock.release()

        return self.reply_text('退票成功')
