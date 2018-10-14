from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import Activity
from adminpage.serializers import activitySerializer


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