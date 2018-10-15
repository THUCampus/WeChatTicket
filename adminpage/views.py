from django.shortcuts import render
from django.contrib import auth
from codex.baseerror import *
from codex.baseview import *
from wechat.models import Activity, Ticket
import datetime
from WeChatTicket.settings import SITE_DOMAIN

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

#删除活动
class activityDelete(APIView):
    def post(self):
        if self.request.user.is_authenticated():
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
        else:
            raise ValidateError('Please login!')

#上传图像并保存到服务器
class imageUpload(APIView):
    def post(self):
        if self.request.user.is_authenticated():
            self.check_input('image')
            image = self.input['image'][0]
            try:
                f = open("static/img/activityImage/" + image.name, "wb")
                for index in image.chunks():
                    f.write(index)
                f.close()
                return SITE_DOMAIN + '/img/activityImage/' + image.name
            except:
                raise ValidateError("Fail to upload image!")
        else:
            raise ValidateError('Please login!')

#活动详情
class activityDetail(APIView):
    #获取活动详情
    def get(self):
        if self.request.user.is_authenticated():
            self.check_input('id')
            id = self.input['id']
            try:
                activity = Activity.objects.get(id=id)
                ticket_List = Ticket.objects.filter(activity_id=activity.id)
                bookedTickets = 0
                usedTickets = 0
                for t in ticket_List:
                    if t.status == Ticket.STATUS_VALID:
                        bookedTickets += 1
                    elif t.status == Ticket.STATUS_USED:
                        usedTickets += 1
                
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
                detail['bookedTickets'] = bookedTickets
                detail['usedTickets'] = usedTickets
                detail['currentTime'] = datetime.datetime.now().timestamp()
                detail['status'] = activity.status
                return detail
            except:
                raise ValidateError("Fail to get activity details!")
        else:
            raise ValidateError('Please login!')

    # #修改活动详情
    def post(self):
        if self.request.user.is_authenticated():
            self.check_input('id', 'name', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart', 'bookEnd', 'totalTickets', 'status')
            id = self.input['id']
            try:
                activity = Activity.objects.get(id=id)
                activity.id = self.input['id']
                activity.name = self.input['name']
                activity.place = self.input['place']
                activity.description = self.input['description']
                activity.pic_url = self.input['picUrl']
                activity.start_time = self.input['startTime']
                activity.end_time = self.input['endTime']
                activity.book_start = self.input['bookStart']
                activity.book_end = self.input['bookEnd']
                activity.total_tickets = self.input['totalTickets']
                activity.status = self.input['status']
                
                activity.save()
            except:
                raise ValidateError("Fail to change activity details!")
        else:
            raise ValidateError('Please login!')