from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User, Activity, Ticket
import json
import time
from datetime import datetime
from django.http import HttpResponse


def replace_split_word_way(k):
    """
    Change the way of word_split from this_is_a_word to thisIsAWord
    :param k:
    :return: changed name;
    """
    words = k.split("_")
    for i in range(1, len(words)):
        words[i] = words[i][0].upper() + words[i][1:]
    return ''.join(words)


def prepare_data_reply(need_keys, *datalist, **replace_data):
    """
    Change the key name and deal with datetime
    :param datalist:
    :return: data for return;
    """
    re_data = {}
    for data in datalist:
        data = data.__dict__
        for k in data:
            if k[0] == '_':
                continue
            new_key = replace_split_word_way(k)
            if new_key not in need_keys:
                continue
            need_keys.remove(new_key)
            if new_key in replace_data:
                new_key = replace_data[new_key]
            value = data[k]
            if isinstance(value, datetime):
                value = int(value.timestamp())
            re_data[new_key] = value
    re_data['currentTime'] = int(time.time())
    return re_data


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        # Here we just think that the user-input is right
        #  if the input is not wrong, accept it.
        if False:
            raise ValidateError('Student ID or password incorrect!')
        if len(User.objects.filter(student_id=self.input['student_id'])) > 0:
            raise ValidateError('A student with the same Student ID exists! Please contact with admin!')

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class ActivityDetail(APIView):

    def get(self):
        self.check_input('id')
        got_activity = Activity.get_by_id(self.input['id'])
        return prepare_data_reply(
            ['name', 'key', 'description', 'startTime', 'endTime', 'place', 'bookStart', 'bookEnd',
             'totalTickets', 'picUrl', 'remainTickets'],
            got_activity
        )


class TicketDetail(APIView):

    def get(self):
        self.check_input('openid', 'ticket')
        got_ticket = Ticket.get_student_ticket(self.input['openid'], self.input['ticket'])
        got_activity = Activity.get_by_id(got_ticket.activity_id)
        return prepare_data_reply(
            ['name', 'place', 'key', 'uniqueId', 'startTime', 'endTime', 'status'],
            got_ticket, got_activity, name='activityName', key='activityKey'
        )
