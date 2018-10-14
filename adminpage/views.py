from django.shortcuts import render
from django.contrib import auth
from codex.baseerror import *
from codex.baseview import *
<<<<<<< HEAD
from wechat.models import Activity
import datetime
=======
>>>>>>> 88b2dfc7bdb6b1db3b19fc1322b34d4b4405a801

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
        try:
            user = auth.authenticate(username=username,password=password)
            auth.login(self.request, user)
        except:
            raise ValidateError("Fail to login!")

<<<<<<< HEAD
#登出
class adminLogout(APIView):
    #登出
=======
class adminLogout(APIView):
>>>>>>> 88b2dfc7bdb6b1db3b19fc1322b34d4b4405a801
    def post(self):
        try:
            auth.logout(self.request)
        except:
<<<<<<< HEAD
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
=======
            raise ValidateError("Fail to logout!")
>>>>>>> 88b2dfc7bdb6b1db3b19fc1322b34d4b4405a801
