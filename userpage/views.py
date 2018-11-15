from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User
from wechat.models import Activity
from wechat.models import Ticket
import time


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        if len(self.input['student_id']) > 32:
            raise ValidateError('Invalid student id')

    def get(self):
        self.check_input('openid')
        try:
            studentId = User.get_by_openid(self.input['openid']).student_id
        except:
            studentId = ''
        return studentId

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class ActivityDetail(APIView):

    def get(self):
        self.check_input('id')
        activity = Activity.get_by_id(self.input['id'])
        if activity.status != Activity.STATUS_PUBLISHED:
            raise LogicError("Activity hasn't been published")
        activity_detail = {
            'name': activity.name,
            'key': activity.key,
            'description': activity.description,
            'startTime': int(time.mktime(activity.start_time.timetuple())),
            'endTime': int(time.mktime(activity.end_time.timetuple())),
            'place': activity.place,
            'bookStart': int(time.mktime(activity.book_start.timetuple())),
            'bookEnd': int(time.mktime(activity.book_end.timetuple())),
            'totalTickets': activity.total_tickets,
            'picUrl': activity.pic_url,
            'remainTickets': activity.remain_tickets,
            'currentTime': int(time.time())
        }
        return activity_detail


class TicketDetail(APIView):

    def get(self):
        self.check_input('openid', 'ticket')
        ticket = Ticket.get_by_uniqueid(self.input['ticket'])
        ticket_detail = {
            'activityName': ticket.activity.name,
            'place': ticket.activity.place,
            'activityKey': ticket.activity.key,
            'uniqueId': ticket.unique_id,
            'startTime': int(time.mktime(ticket.activity.start_time.timetuple())),
            'endTime': int(time.mktime(ticket.activity.end_time.timetuple())),
            'currentTime': int(time.time()),
            'status': ticket.status
        }
        return ticket_detail
