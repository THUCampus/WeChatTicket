# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler
from wechat.models import User,Activity,Ticket

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
            'Title': 'wtf',
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


class BookActivityHandler(WeChatHandler):

    def check(self):
        if self.is_event('CLICK'):
            event_key = self.view.event_keys['book_header']
            event_key += self.input['EventKey'][len(event_key):]
            return self.is_event_click(event_key)
        return False

    def handle(self):
        if not self.user.student_id:
            return self.reply_text('对不起，您尚未绑定，无法抢票')

        act_id = self.input['EventKey'][len(self.view.event_keys['book_header']):]
        activity = self.get_activity(act_id)
        if not activity:
            return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')
        if activity.remain_tickets > 0:
            ticket = Ticket.objects.filter(student_id = self.user.student_id, activity = activity)
            if not ticket:
                unique_id = self.user.student_id + act_id
                Ticket.objects.create(student_id = self.user.student_id, uniqueId = unique_id,
                activity = activity, status = Ticket.STATUS_VALID, activityName = activity.name,
                place = activity.place, activityKey = activity.key,startTime = activity.start_time.timestamp(),
                endTime = activity.end_time.timestamp(),currentTime = datetime.datetime.now().timestamp())
                activity.remain_tickets -= 1
                return self.reply_text('抢票成功')
            else:
                return self.reply_text('对不起，您已经购买过本场活动的票')
        return self.reply_single_news({
            'Title': activity.name,
            'Description': activity.description,
            'Url': self.url_book(act_id),
            'PicUrl': activity.pic_url,
        })


class BookWhatHandler(WeChatHandler):
    def check(self):
        return self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        activities = self.get_activities()
        if not activities:
            return self.reply_text('对不起，现在没有正在抢票的活动')
        articles = []
        for activity in activities:
            articles.append({
                'Title': activity.name,
                'Description': activity.description,
                'Url': self.url_book(activity.id),
                'PicUrl': activity.pic_url,
            })
        return self.reply_news(articles)


class GetTicketHandler(WeChatHandler):
    def check(self):
        return self.is_text('查票') or self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        tickets = self.get_tickets()
        if not tickets:
            return self.reply_text('对不起，当前没有已经购买的票')
        articles = []
        for ticket in tickets:
            articles.append({
                'Title':ticket.activity.name,
                'Description':ticket.activity.description,
                'Url':self.url_ticket(ticket.unique_id),
                'PicUrl':ticket.activity.pic_url,
            })
        return self.reply_news(articles)