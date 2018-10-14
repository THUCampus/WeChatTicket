from django.shortcuts import render
from django.contrib import auth
from codex.baseerror import *
from codex.baseview import *
from wechat.models import Activity
import datetime

# Create your views here.

# 登录
class adminLogin(APIView):
    #获取登录状态
    def get(self):
        if not self.request.user.is_authenticated():
            raise ValidateError(self.input)

    #验证用户名和密码登陆（django——superuser）
    def post(self):
        self.check_input('username', 'password')
        username = self.input['username']
        password = self.input['password']
        # try:
        #     user = auth.models.User.objects.filter(username__exact = username)
        #     if not user:
        #         raise ValidateError("User name does not exit!")
        #     if user.first().password != password:
        #         raise ValidateError("User password error!")
        #     user = auth.authenticate(username=username,password=password)
        #     auth.login(self.request, user)
        # except:
        #     raise ValidateError("System error!")
        try:
            user = auth.authenticate(username=username,password=password)
            auth.login(self.request, user)
        except:
            raise ValidateError("Fail to login!")

#登出
class adminLogout(APIView):
    #登出
    def post(self):
        try:
            auth.logout(self.request)
        except:
            raise ValidateError("Fail to logout!")

#活动列表
class activityList(APIView):
    #获取活动列表
    def get(self):
        if self.request.user.is_authenticated():
            activity_List = []
            activites = Activity.objects.all()
            for activity in activites:
                if activity.status >= 0:
                    info = {}
                    info['id'] = activity.id
                    info['name'] = activity.name
                    info['description'] = activity.description
                    info['startTime'] = activity.start_time.timestamp()
                    info['endTime'] = activity.end_time.timestamp()
                    info['place'] = activity.place
                    info['bookStart'] = activity.book_start.timestamp()
                    info['bookEnd'] = activity.book_end.timestamp()
                    info['currentTime'] = datetime.datetime.now().timestamp()
                    info['status'] = activity.status
                    activity_List.append(info)
            return activity_List
        else:
            raise ValidateError('Please login!')

#创建活动
class activityCreate(APIView):
    def post(self):
        if self.request.user.is_authenticated():
            self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime', 'endTime', 
            'bookStart', 'bookEnd', 'totalTickets', 'status')
            
            name = self.input['name']
            key = self.input['key']
            place = self.input['place']
            description = self.input['description']
            pic_url = self.input['picUrl']
            start_time = self.input['startTime']
            end_time = self.input['endTime']
            book_start = self.input['bookStart']
            book_end = self.input['bookEnd']
            total_tickets = self.input['totalTickets']
            remain_tickets = self.input['totalTickets']
            status = self.input['status']
            try:
                new = Activity(name=name, key=key, place=place, 
                description=description, pic_url=pic_url, start_time=start_time, 
                end_time=end_time, book_start=book_start, book_end=book_end, 
                total_tickets=total_tickets, remain_tickets=remain_tickets, status=status)
                new.save()
                return new.id
            except:
                raise ValidateError('Create activity error!')
        else:
            raise ValidateError('Please login!')

# #删除活动
class activityDelete(APIView):
    def post(self):
        self.check_input('id')
        id = self.input['id']
        activity = Activity.objects.filter(id__exact = id)
        if activity:
            try:
                activity.delete()
            except:
                raise ValidateError("System error!")
        else:
            raise ValidateError("ID does not exit!")