from django.shortcuts import render
from codex.baseerror import *
from codex.baseview import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from wechat.models import Activity
from wechat.models import Ticket
from wechat.views import CustomWeChatView
from WeChatTicket.settings import SITE_DOMAIN
import time
from datetime import datetime, timedelta
# Create your views here.


class Login(APIView):

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('User not logged in')
        return 0

    def post(self):
        self.check_input('username', 'password')
        username = self.input['username']
        password = self.input['password']
        user = authenticate(username=username, password=password)

        if not username:
            raise ValidateError('Username is empty！')
        if not password:
            raise ValidateError('Password is empty！')
        if not User.objects.filter(username=username):
            raise ValidateError('Username does not exist！')
        if not user:
            raise ValidateError('Wrong password！')

        if user.is_active:
            login(self.request, user)
            return 0


class Logout(APIView):

    def post(self):
        if self.request.user.is_authenticated():
            logout(self.request)
        else:
            raise ValidateError('Logout failed！User has not logged in.')


class ActivityList(APIView):

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('User not logged in！')

        activityList = Activity.objects.all()
        data = []
        for item in activityList:
            if item.status >= 0:
                temp = {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'startTime': int(time.mktime(item.start_time.timetuple())),
                    'endTime': int(time.mktime(item.end_time.timetuple())),
                    'place': item.place,
                    'bookStart': int(time.mktime(item.book_start.timetuple())),
                    'bookEnd': int(time.mktime(item.book_end.timetuple())),
                    'currentTime': int(time.time()),
                    'status': item.status,
                }
                data.append(temp)
            else:
                continue
        return data


class ActivityDelete(APIView):

    def post(self):
        self.check_input('id')
        activity = Activity.get_by_id(self.input['id'])
        activity.delete()


class ActivityCreate(APIView):
    def post(self):
        self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
        if not self.request.user.is_authenticated():
            raise ValidateError('User not logged in！')
        new_activity = Activity(
            name = self.input['name'],
            key = self.input['key'],
            place = self.input['place'],
            description = self.input['description'],
            pic_url = self.input['picUrl'],
            start_time = datetime.strptime(self.input['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8),
            end_time = datetime.strptime(self.input['endTime'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8),
            book_start = datetime.strptime(self.input['bookStart'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8),
            book_end = datetime.strptime(self.input['bookEnd'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8),
            remain_tickets = self.input['totalTickets'],
            total_tickets = self.input['totalTickets'],
            status = self.input['status']
        )
        new_activity.save()
        return new_activity.id


class ActivityDetail(APIView):

    def get(self):
        self.check_input('id')
        if not self.request.user.is_authenticated():
            raise ValidateError('User has not logged in.')
        activity = Activity.get_by_id(self.input['id'])
        usedTickets = 0
        for ticket in activity.ticket_set.all():
            if ticket.status == Ticket.STATUS_USED:
                usedTickets += 1
        data = {
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
            'bookedTickets': activity.total_tickets - activity.remain_tickets,
            'usedTickets': usedTickets,
            'currentTime': int(time.time()),
            'status': activity.status
        }
        return data

    def post(self):
        self.check_input('id', 'name', 'place', 'description', 'picUrl',
                         'startTime', 'endTime', 'bookStart', 'bookEnd',
                         'totalTickets', 'status')
        if not self.request.user.is_authenticated():
            raise ValidateError('User has not logged in.')
        activity = Activity.get_by_id(self.input['id'])
        if activity.status == Activity.STATUS_PUBLISHED:
            if activity.name != self.input['name']:
                raise LogicError('Cannot modify the name of a published activity ')
            if activity.place != self.input['place']:
                raise LogicError('Cannot modify the place of a published activity')
            if activity.book_start != (datetime.strptime(self.input['bookStart'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)):
                raise LogicError('Cannot modify the bookStart time of a published activity')
            if self.input['status'] != 1:
                raise LogicError('you cannot stage published activity')

        if int(time.mktime(activity.end_time.timetuple())) < int(time.time()):
            if activity.start_time != (datetime.strptime(self.input['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)):
                raise LogicError('Cannot modify startTime of a activity ended')
            if activity.end_time != (datetime.strptime(self.input['endTime'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)):
                raise LogicError('Cannot modify endTime of a activity ended')

        if int(time.mktime(activity.start_time.timetuple())) < int(time.time()):
            if activity.book_end != (datetime.strptime(self.input['bookEnd'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)):
                raise LogicError('Cannot modify bookEnd time of a activity started')

        if int(time.mktime(activity.book_start.timetuple())) < int(time.time()):
            if activity.total_tickets != self.input['totalTickets']:
                raise LogicError('Cannot modify totalTickets after book_start')

        activity.name = self.input['name']
        activity.place = self.input['place']
        activity.description = self.input['description']
        activity.pic_url = self.input['picUrl']
        activity.start_time = (datetime.strptime(self.input['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8))
        activity.end_time = (datetime.strptime(self.input['endTime'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8))
        activity.book_start = (datetime.strptime(self.input['bookStart'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8))
        activity.book_end = (datetime.strptime(self.input['bookEnd'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8))
        activity.total_tickets = self.input['totalTickets']
        activity.status = self.input['status']

        activity.save()


class ActivityMenu(APIView):

    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('User has not logged in.')
        activityListAll = Activity.objects.all()
        wechat_menu = CustomWeChatView.lib.get_wechat_menu()
        if len(wechat_menu) >= 2:
            actiListInMenu = wechat_menu[1]['sub_button']
        else:
            actiListInMenu = []
        data = []
        for acti in activityListAll:
            if acti.status == Activity.STATUS_DELETED:
                continue
            temp = {
                'id': acti.id,
                'name': acti.name,
                'menuIndex': 0
            }
            i = 0
            while i < len(actiListInMenu):
                if actiListInMenu[i]['name'] == acti.name:
                    temp['menuIndex'] = i+1
                    break
                i += 1

            data.append(temp)
        return data

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError('User has not logged in.')
        activityList = []
        for activity_id in self.input:
            activity = Activity.get_by_id(activity_id)
            activity.status = Activity.STATUS_PUBLISHED
            activity.save()
            activityList.append(activity)
        CustomWeChatView.update_menu(activityList)


class ImageUpload(APIView):

    def post(self):
        self.check_input('image')
        if not self.request.user.is_authenticated():
            raise ValidateError('User has not logged in.')
        image = self.input['image'][0]
        try:
            with open('static/media/img/' + image.name, 'wb') as img_file:
                for i in image.chunks():
                    img_file.write(i)
            return SITE_DOMAIN + '/media/img/' + image.name
        except:
            raise ValidateError('Fail to upload image')


class ActivityCheckin(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("User not logged in!")
        self.check_input('actId')
        try:
            activity = Activity.objects.get(id=self.input['actId'])
        except:
            raise LogicError('actID error！Activity not found')
        try:
            if "ticket" in self.input:
                ticket = Ticket.objects.get(activity=activity,unique_id=self.input['ticket'])
            elif 'studentId' in self.input.keys():
                ticket = Ticket.objects.get(activity=activity,student_id=self.input['studentId'])
        except:
            raise LogicError("no ticket！")

        if ticket.status == Ticket.STATUS_CANCELLED:
            raise LogicError(" ticket canceled!")
        elif ticket.status == Ticket.STATUS_USED:
            raise LogicError("ticket used！")
        elif ticket.status == Ticket.STATUS_VALID:
            data = {
                'ticket': ticket.unique_id,
                'studentId': ticket.student_id
            }
            ticket.status = Ticket.STATUS_USED
            ticket.save()
            return data
        else:
            raise ValidateError("fail to checkin!")
