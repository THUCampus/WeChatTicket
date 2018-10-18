from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import Activity, Ticket
from adminpage.serializers import activitySerializer

from django.conf import settings
from django.utils import timezone
from wechat.views import CustomWeChatView

import os
import time



class ActivityList(APIView):

    def get(self):

        if not self.request.user.is_authenticated():
            raise ValidateError(self.input)

        activity_set = Activity.objects.exclude(status = Activity.STATUS_DELETED)
        activity_list = []
        for activity in activity_set:
            activity_serial = activitySerializer(activity)
            activity_list.append(activity_serial)

        return activity_list


class ActivityDelete(APIView):

    def post(self):
        self.check_input('id')
        try:
            activity_to_del = Activity.objects.get(id=self.input['id'])
        except Activity.DoesNotExist:
            raise DatabaseError(self.input)
        if activity_to_del.status == Activity.STATUS_DELETED:
            raise LogicError(self.input)
        activity_to_del.status = Activity.STATUS_DELETED
        activity_to_del.save()


class ActivityCreate(APIView):

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError(self.input)

        self.check_input('name', 'key', 'place', 'picUrl', 'startTime',
                         'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
        try:
            print(self.input['bookStart'])
            Activity.objects.create(name = self.input['name'],
                                    key = self.input['key'],
                                    place = self.input['place'],
                                    description = self.input['description'],
                                    start_time = self.input['startTime'],
                                    pic_url = self.input['picUrl'],
                                    end_time = self.input['endTime'],
                                    book_start = self.input['bookStart'],
                                    book_end = self.input['bookEnd'],
                                    total_tickets = self.input['totalTickets'],
                                    status = self.input['status'],
                                    remain_tickets = self.input['totalTickets'])
        except Exception as e:
            raise DatabaseError(self.input)


class ImageUpload(APIView):

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("not login")

        img = self.input['image'][0]
        img_path = os.path.join(settings.IMAGE_ROOT, img.name)

        try:
            with open(img_path, 'wb') as imgp:
                for info in img.chunks():
                    imgp.write(info)
            img_url = settings.SITE_DOMAIN + '/img/' + img.name
            return img_url

        except Exception as e:
            raise FileError("upload file with name %s failed" % img.name)


class ActivityDetail(APIView):



    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("not login")

        try:
            activity = Activity.objects.get(id = self.input['id'])
            activity_detail = {}
            activity_detail['name'] = activity.name
            activity_detail['key'] = activity.key
            activity_detail['description'] = activity.description
            activity_detail['startTime'] = activity.start_time.timestamp()
            activity_detail['endTime'] = activity.end_time.timestamp()
            activity_detail['place'] = activity.place
            activity_detail['bookStart'] = activity.book_start.timestamp()
            activity_detail['bookEnd'] = activity.book_end.timestamp()
            activity_detail['totalTickets'] = activity.total_tickets
            activity_detail['picUrl'] = activity.pic_url
            activity_detail['bookedTickets'] = activity.total_tickets - activity.remain_tickets
            activity_detail['usedTickets'] = Ticket.objects.filter(activity_id=activity.id, status=Ticket.STATUS_USED).count()
            activity_detail['currentTime'] = time.time()
            activity_detail['status'] = activity.status

            return activity_detail

        except Exception as e:
            raise DatabaseError("get detail from id %d failed" % int(self.input['id']))

    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("not login")

        self.check_input('id', 'name', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart', 'bookEnd',
                         'totalTickets', 'status')

        try:
            activity = Activity.objects.get(id = self.input['id'])
            activity_status = activity.status
            current_time = time.time()

            activity.description = self.input['description']
            activity.pic_url = self.input['picUrl']

            if activity_status == Activity.STATUS_SAVED:
                activity.name = self.input['name']
                activity.place = self.input['place']
                activity.book_start = self.input['bookStart']
                activity.status = self.input['status']
                activity.save()
                activity = Activity.objects.get(id=self.input['id'])

            if current_time < activity.book_start.timestamp():
                activity.total_tickets = self.input['totalTickets']

            if current_time < activity.start_time.timestamp():
                activity.book_end = self.input['bookEnd']

            if current_time < activity.end_time.timestamp():
                activity.start_time = self.input['startTime']
                activity.end_time = self.input['endTime']

            activity.save()

        except Exception as e:
            raise DatabaseError('change detailed with id %d failed' % self.input['id'])


class ActivityMenu(APIView):
    def get(self):

        if not self.request.user.is_authenticated():
            raise ValidateError("not login")
        try:
            current_menu = CustomWeChatView.lib.get_wechat_menu()
            existed_button = list()
            for btn in current_menu:
                if btn['name'] == '抢票':
                    existed_button += btn.get('sub_button', list())
            activity_ids = list()
            for btn in existed_button:
                if 'key' in btn:
                    activity_id = btn['key']
                    if activity_id.startswith(CustomWeChatView.event_keys['book_header']):
                        activity_id = activity_id[len(CustomWeChatView.event_keys['book_header'])]
                    if activity_id and activity_id.isdigit():
                        activity_ids.append(int(activity_id))
            activitys = []
            activity_in = Activity.objects.filter(id__in = activity_ids, book_start__lt=timezone.now()
                                                  , book_end__gt=timezone.now(), status=Activity.STATUS_PUBLISHED)
            index = 1
            for activity in activity_in:
                activitys.append({'id': activity.id, 'name': activity.name, 'menuIndex': index})
                index += 1
            activity_nin = Activity.objects.exclude(id__in = activity_ids, status__lt = Activity.STATUS_SAVED)
            for activity in activity_nin:
                activitys.append({'id': activity.id, 'name': activity.name, 'menuIndex': 0})
            return activitys
        except Exception as e:
            raise MenuError("get menu failed")

    def post(self):

        if not self.request.user.is_authenticated():
            raise ValidateError("not login")

        try:
            activity_id_list = self.input
            activity_list = []
            for id in activity_id_list:
                activity = Activity.objects.get(id=id)
                activity_list.append(activity)
            CustomWeChatView.update_menu(activity_list)

        except Exception as e:
            raise MenuError("update menu failed")


class ActivityCheckin(APIView):
    def post(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("not login")
        self.check_input('actId')
        current_time = time.time()
        try:
            activity = Activity.objects.get(id=self.input['actId'])
            # if 'ticket' in self.input:
            #     ticket = Ticket.objects.get(unique_id=self.input['ticket'])
            # else:
            #     ticket = Ticket.objects.get(student_id=self.input['studentId'])
            if 'studentId' in self.input:
                ticket = Ticket.objects.get(student_id=self.input['studentId'])
            else:
                ticket = Ticket.objects.get(unique_id=self.input['ticket'])

        except Exception as e:
            raise DatabaseError("get activity or ticket failed")

        if current_time > activity.end_time.timestamp():
            raise LogicError("activity has ended")

        if ticket.status == Ticket.STATUS_USED:
            raise LogicError("ticket has been used")

        if ticket.status == Ticket.STATUS_CANCELLED:
            raise LogicError("ticket has been canceled")

        if ticket.activity_id != activity.id:
            raise LogicError("ticket doesn't match activity")

        ticket.status = Ticket.STATUS_USED
        ticket.save()

        data = {'ticket': ticket.unique_id, 'studentId': ticket.student_id}
        return data
