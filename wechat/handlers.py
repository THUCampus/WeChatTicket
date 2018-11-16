# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import User,Activity,Ticket
import datetime
from django.db import transaction
import uuid

__author__ = "Epsirom"


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

#抢票
class BookActivityHandler(WeChatHandler):

    def check(self):
        if self.is_event('CLICK'):
            event_key = self.view.event_keys['book_header']
            event_key += self.input['EventKey'][len(event_key):]
            return self.is_event_click(event_key)
        else:
            return self.is_text('抢票')
        return False

    def handle(self):
        if not self.user.student_id:
            return self.reply_text(self.get_message('bind_account'))

        currentTime = datetime.datetime.now().timestamp()
        if self.is_event('CLICK'):
            event_key = self.view.event_keys['book_header']
            event_key += self.input['EventKey'][len(event_key):]
            if self.is_event_click(event_key):
                act_id = self.input['EventKey'][len(self.view.event_keys['book_header']):]
                activity = self.get_activity(act_id)
                if not activity:
                    return self.reply_text('对不起，没有该项活动')
                if currentTime < activity.book_start.timestamp():
                    return self.reply_text('对不起，还未开放抢票')
                if currentTime > activity.book_end.timestamp():
                    return self.reply_text('对不起，抢票已经截止')
                #check if the student has book a ticket:
                if Ticket.objects.filter(student_id = self.user.student_id, activity = activity, status = Ticket.STATUS_VALID):
                    return self.reply_text('一个人只能抢一张票哦 ^口..口^')
                if Ticket.objects.filter(student_id = self.user.student_id, activity = activity, status = Ticket.STATUS_USED):
                    return self.reply_text('您已经抢过该活动的票且使用过')
                #lock!lock!lock!
                ticket = self.book_ticket(act_id)
                activity = self.get_activity(act_id)
                if ticket:
                    return self.reply_single_news({
                        'Title':activity.name,
                        'Description':'抢票成功',
                        'Url':ticket,
                        'PicUrl':activity.pic_url,
                    })
                else:
                    return self.reply_text('没有多的票了！请自行尝试劝退抢到票的朋友们~')
            else:
                return False

        elif self.is_text('抢票'):
            query = self.input['Content'][3:]
            activity = Activity.objects.filter(key = query).first()
            if not activity:
                activity = Activity.objects.filter(name = query).first()
                if not activity:
                    return self.reply_text('对不起，没有该项活动')
            if currentTime < activity.book_start.timestamp():
                return self.reply_text('对不起，还未开放抢票')
            if currentTime > activity.book_end.timestamp():
                return self.reply_text('对不起，抢票已经截止')
            if Ticket.objects.filter(student_id = self.user.student_id, activity = activity, status = Ticket.STATUS_VALID):
                return self.reply_text('一个人只能抢一张票哦 ^口..口^')
            if Ticket.objects.filter(student_id = self.user.student_id, activity = activity, status = Ticket.STATUS_USED):
                return self.reply_text('您已经抢过该活动的票且使用过')
            if activity.remain_tickets == 0:
                return self.reply_text('没有多的票了！请自行尝试劝退抢到票的朋友们~')
            unique_id = uuid.uuid5(uuid.NAMESPACE_DNS,self.user.student_id + activity.name + str(currentTime))
            Ticket.objects.create(student_id = self.user.student_id, unique_id = unique_id,
            activity = activity, status = Ticket.STATUS_VALID)
            activity.remain_tickets -= 1
            activity.save()
            ticket = self.url_ticket(unique_id)
            return self.reply_single_news({
                'Title':activity.name,
                'Description':'抢票成功',
                'Url':ticket,
                'PicUrl':activity.pic_url,
                })


 #抢啥   
class BookWhatHandler(WeChatHandler):
    def check(self):
        return self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):

        activities = self.get_activities()
        if not activities:
            return self.reply_text('对不起，现在没有正在抢票的活动')
        articles = []
        currentTime = datetime.datetime.now().timestamp()
        for activity in activities:
            if currentTime < activity.end_time.timestamp():
                articles.append({
                    'Title': activity.name,
                    'Description': activity.description,
                    'Url': self.url_book(activity.id),
                    'PicUrl': activity.pic_url,
                })
        if len(articles) > 0:
            return self.reply_news(articles)
        else:
            return self.reply_text('对不起，现在没有正在抢票的活动')

#查票
class GetTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        if self.is_event_click(self.view.event_keys['get_ticket']):
            tickets = self.get_tickets()
            if not tickets:
                return self.reply_text('对不起，当前没有已经购买的票')
            articles = []
            currentTime = datetime.datetime.now().timestamp()
            for ticket in tickets:
                if ticket.status == Ticket.STATUS_VALID:
                    str1 = '有效票未使用'
                    if currentTime > ticket.activity.end_time.timestamp():
                        str1 += '   活动已结束'
                elif ticket.status == Ticket.STATUS_USED:
                    str1 = '有效票已使用'
                else:
                    str1 = '已退票'
                self.logger.warn(str1)
                articles.append({
                    'Title':ticket.activity.name + '   ' + str1,
                    'Description':'电子票查看',
                    'Url':self.url_ticket(ticket.unique_id),
                    'PicUrl':ticket.activity.pic_url,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                })
            return self.reply_news(articles)
        else:
            query = self.input['Content'][3:]
            activity = Activity.objects.filter(key = query).first()
            if not activity:
                activity = Activity.objects.filter(name = query).first()
                if not activity:
                    return self.reply_text('对不起，没有这场活动')
            tickets = Ticket.objects.filter(student_id = self.user.student_id, activity = activity)
            if not tickets:
                return self.reply_text('对不起，当前没有已经购买的有效票')
            for ticket in tickets:
                if ticket.status == Ticket.STATUS_VALID:
                    currentTime = datetime.datetime.now().timestamp()
                    str1 = '有效票未使用'
                    if currentTime > ticket.activity.end_time.timestamp():
                        str1 += '   活动已结束'
                    return self.reply_single_news({
                    'Title':ticket.activity.name + '   ' + str1,
                    'Description':'电子票查看',
                    'Url':self.url_ticket(ticket.unique_id),
                    'PicUrl':ticket.activity.pic_url,
                    })
            return self.reply_text('对不起，当前没有已经购买的有效票')

#取票
class PickTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('取票')

    def handle(self):
        query = self.input['Content'][3:]
        activity = Activity.objects.filter(key = query).first()
        if not activity:
            activity = Activity.objects.filter(name = query).first()
            if not activity:
                return self.reply_text('对不起，没有这场活动')
        tickets = Ticket.objects.filter(student_id = self.user.student_id, activity = activity)
        if not tickets:
            return self.reply_text('对不起，当前没有已经购买的有效票')
        for ticket in tickets:
            if ticket.status == Ticket.STATUS_VALID:
                currentTime = datetime.datetime.now().timestamp()
                str1 = '有效票未使用'
                if currentTime > ticket.activity.end_time.timestamp():
                    str1 += '   活动已结束'
                return self.reply_single_news({
                'Title':ticket.activity.name + '   ' + str1,
                'Description':'电子票查看',
                'Url':self.url_ticket(ticket.unique_id),
                'PicUrl':ticket.activity.pic_url,
                })
        return self.reply_text('对不起，当前没有已经购买的有效票')

#退票
class CancelTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('退票')
    
    def handle(self):
        query = self.input['Content'][3:]
        with transaction.atomic(): 
            activity = Activity.objects.select_for_update().filter(key = query).first()
            if not activity:
                activity = Activity.objects.select_for_update().filter(name = query).first()
                if not activity:
                    return self.reply_text('对不起，没有这场活动')
            ticket = Ticket.objects.filter(student_id = self.user.student_id, activity = activity, status = Ticket.STATUS_VALID).first()
            if not ticket:
                return self.reply_text('对不起，您没有本场活动未使用的有效票')
            else:
                currentTime = datetime.datetime.now().timestamp()
                if currentTime > ticket.activity.end_time.timestamp():
                    return self.reply_text('对不起，活动已经结束，不能退票')
                activity.remain_tickets += 1
                activity.save()
                ticket.status = Ticket.STATUS_CANCELLED
                ticket.save()
                return self.reply_single_news({
                    'Title':ticket.activity.name,
                    'Description':'电子票退票成功',
                    'Url':self.url_ticket(ticket.unique_id),
                    'PicUrl':ticket.activity.pic_url,
                    })
            if Ticket.objects.filter(student_id = self.user.student_id, activity = activity, status = Ticket.STATUS_USED).first():
                return self.reply_text('对不起，这张票您已经使用过')
            if Ticket.objects.filter(student_id = self.user.student_id, activity = activity, status = Ticket.STATUS_CANCELLED).first():
                return self.reply_text('这张票已经退票过')
            return self.reply_text('对不起，您未购买过本场活动的票')
            
