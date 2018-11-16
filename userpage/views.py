from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User,Activity,Ticket
import re
import datetime


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        self.check_input('student_id')
        student_id = self.input['student_id']
        if User.objects.filter(student_id=student_id):
            raise ValidateError('该学号已被占用!')
        #check the validity of student_id:
        if re.match('^[0-9]{10}$',student_id):
            #check the year
            year = int(re.match('^[0-9]{4}',student_id).group(0))
            if (year < 1911 or year > datetime.datetime.now().year):
                raise ValidateError('无效学号!')
        else:
            raise ValidateError('无效学号!')

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()

class UserActivityDetail(APIView):
    def get(self):
        self.check_input('id')
        try:
            activity_list = Activity.objects.filter(id = self.input['id'])
            if not activity_list:
                raise ValidateError('Not found')
            activity = activity_list[0]
            if(activity.status != Activity.STATUS_PUBLISHED):
                raise ValidateError("活动已截止")
            detail = {}
            detail['name'] = activity.name
            detail['key'] = activity.key
            detail['description'] = activity.description
            detail['startTime'] = activity.start_time.timestamp()
            detail['endTime'] = activity.end_time.timestamp()
            detail['place'] = activity.place
            detail['bookStart'] = activity.book_start.timestamp()
            detail['bookEnd'] = activity.book_end.timestamp()
            detail['totalTickets'] = activity.total_tickets
            detail['picUrl'] = activity.pic_url
            detail['remainTickets'] = activity.remain_tickets
            detail['currentTime'] = datetime.datetime.now().timestamp()
            return detail
        except:
            raise ValidateError('Activity not found!')

class TicketDetail(APIView):

    def get(self):
        self.check_input('openid','ticket')
        user = User.objects.filter(open_id=self.input['openid'])
        if not user:
            raise LogicError('User not found')
        ticketlist = Ticket.objects.filter(student_id=user[0].student_id,unique_id=self.input['ticket'])
        if not ticketlist:
            errormsg = user[0].student_id+' '+self.input['ticket']
            raise LogicError(errormsg)
        ticket = ticketlist[0]
        activity = ticket.activity
        detail = {
            'activityName': activity.name,
            'place': activity.place,
            'activityKey': activity.key,
            'uniqueId': ticket.unique_id,
            'startTime': activity.start_time.timestamp(),
            'endTime': activity.end_time.timestamp(),
            'currentTime': datetime.datetime.now().timestamp(),
            'status': ticket.status,
        }
        return detail
            