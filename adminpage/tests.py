import json
import copy

from django.utils import timezone
from datetime import datetime
from django.test import Client, TestCase
from django.contrib.auth.models import User

from wechat.models import Activity, Ticket
from codex.baseerror import *
from adminpage.views.admin import *
from adminpage.views.activity import *

adminForTest = {"username": "admin", "email": "admin@test.com", "password": "admin_psw"}
userForTest = {"username": "user", "email": "user@test.com", "password": "user_psw"}
wrongUserForTest = {"username": "user", "email": "user@test.com", "password": "user_wrong_psw"}

deleted_activity = Activity(id=1, name='deleted', key='key', place='place',
                            description='description', start_time=timezone.now(), pic_url="pic_url",
                            end_time=timezone.now(), book_start=timezone.now(), book_end=timezone.now(),
                            total_tickets=100, status=Activity.STATUS_DELETED, remain_tickets=100)

saved_activity = Activity(id=2, name='saved', key='key', place='place',
                          description='description', start_time=timezone.now(), pic_url="pic_url",
                          end_time=timezone.now(), book_start=timezone.now(), book_end=timezone.now(),
                          total_tickets=100, status=Activity.STATUS_SAVED, remain_tickets=100)

published_activity = Activity(id=3, name='published', key='key', place='place',
                              description='description', start_time=timezone.now(), pic_url="pic_url",
                              end_time=timezone.now(), book_start=timezone.now(), book_end=timezone.now(),
                              total_tickets=100, status=Activity.STATUS_PUBLISHED, remain_tickets=100)

published_activity_dic = {"id": 3, "name": 'published', "key":'key', "place":'place',
                        "description":'description', "startTime":timezone.now(), "picUrl":"pic_url",
                         "endTime": timezone.now(), "bookStart":timezone.now(), "bookEnd":timezone.now(),
                          "totalTickets":100, "status":Activity.STATUS_PUBLISHED, "remainTickets":100}


class GetLoginStatusTest(TestCase):
    "test getting login status"
    def setUp(self):
        User.objects.create_superuser(adminForTest['username'],
                                      adminForTest['email'],
                                      adminForTest['password'])
        User.objects.create_user(userForTest['username'],
                                 userForTest['email'],
                                 userForTest['password'])

    def tearDown(self):
        pass

    def test_not_login(self):
        c = Client()
        response = c.get('/api/a/login')
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 3)

    def test_already_login(self):
        c = Client()
        c.post('/api/a/login', userForTest)
        response = c.get('/api/a/login')
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)


class LoginTest(TestCase):
    "test logging in"
    def setUp(self):
        User.objects.create_superuser(adminForTest['username'],
                                      adminForTest['email'],
                                      adminForTest['password'])
        User.objects.create_user(userForTest['username'],
                                 userForTest['email'],
                                 userForTest['password'])

    def tearDown(self):
        pass

    def test_admin_login(self):
        c = Client()
        response = c.post('/api/a/login', adminForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

    def test_user_login(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

    def test_wrong_password_login(self):
        admin_login = AdminLogin()
        admin_login.input = {}
        admin_login.input = wrongUserForTest
        self.assertRaises(ValidateError, admin_login.post)

    def test_no_password_login(self):
        admin_login = AdminLogin()
        admin_login.input = {}
        admin_login.input['username'] = userForTest['username']
        self.assertRaises(InputError, admin_login.post)


class LogoutTest(TestCase):
    "test logging out"
    def setUp(self):
        User.objects.create_superuser(adminForTest['username'],
                                      adminForTest['email'],
                                      adminForTest['password'])
        User.objects.create_user(userForTest['username'],
                                 userForTest['email'],
                                 userForTest['password'])

    def tearDown(self):
        pass

    def test_user_logout(self):
        c = Client()
        c.post('/api/a/login', userForTest)
        response = c.post('/api/a/logout', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)


class ActivityDeleteTest(TestCase):

    def setUp(self):
        User.objects.create_superuser(adminForTest['username'],
                                      adminForTest['email'],
                                      adminForTest['password'])
        User.objects.create_user(userForTest['username'],
                                 userForTest['email'],
                                 userForTest['password'])
        deleted_activity.save()
        saved_activity.save()
        published_activity.save()

    def tearDown(self):
        Activity.objects.get(id=1).delete()
        Activity.objects.get(id=2).delete()
        Activity.objects.get(id=3).delete()

    def test_activity_list(self):
        c = Client()
        c.post('/api/a/login', adminForTest)
        response = c.get('/api/a/activity/list')
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        response_list = response_dict['data']
        self.assertEqual(len(response_list), 2)

    def test_activity_delete_success(self):
        c = Client()
        c.post('/api/a/login', adminForTest)
        response = c.post('/api/a/activity/delete', {"id": "2"})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

    def test_activity_delete_again(self):
        activity_delete = ActivityDelete()
        activity_delete.input = {}
        activity_delete.input['id'] = 1
        self.assertRaises(LogicError, activity_delete.post)


class ActivityCreateTest(TestCase):
    def setUp(self):
        User.objects.create_superuser(adminForTest['username'],
                                      adminForTest['email'],
                                      adminForTest['password'])
        User.objects.create_user(userForTest['username'],
                                 userForTest['email'],
                                 userForTest['password'])

    def tearDown(self):
        pass

    def test_activity_create(self):
        c = Client()
        c.post('/api/a/login', adminForTest)
        response = c.post('/api/a/activity/create', published_activity_dic)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)


class ImageUploadTest(TestCase):
    # TODO:
    # 1.上传文件成功
    # 2.未登录
    def setUp(self):
        User.objects.create_superuser(adminForTest['username'],
                                      adminForTest['email'],
                                      adminForTest['password'])
        User.objects.create_user(userForTest['username'],
                                 userForTest['email'],
                                 userForTest['password'])

    def test_upload(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)
        pic_root = os.path.join(settings.BASE_DIR, 'test/azuna.jpg')
        with open(pic_root, 'rb') as p:
            response = c.post('/api/a/image/upload', {'image': p})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

    def test_upload_without_logging_in(self):
        c = Client()
        pic_root = os.path.join(settings.BASE_DIR, 'test/azuna.jpg')
        with open(pic_root, 'rb') as p:
            c.post('/api/a/image/upload', {'image': p})

class ActivityDetailTest(TestCase):
    # TODO:
    # 0.获取活动详情成功
    # 1.修改活动详情成功
    # 2.修改活动详情失败（已发布）
    # 3.修改活动详情失败（抢票已开始）
    # 4.修改活动详情失败（活动已开始）
    # 5.修改活动详情失败（活动已结束）

    DeletedID = 1
    SavedID = 2
    PublishedID = 3
    BookStartID = 4
    StartedID = 5
    EndedID = 6

    def setUp(self):
        User.objects.create_superuser(adminForTest['username'],
                                      adminForTest['email'],
                                      adminForTest['password'])
        User.objects.create_user(userForTest['username'],
                                 userForTest['email'],
                                 userForTest['password'])

        deleted_activity.save()
        saved_activity.save()
        published_activity.save()

        n = 10

        for i in range(n):
            ticket = Ticket(student_id='Valid_' + str(i), unique_id='Valid_' + str(i), activity_id=published_activity.id,
                            status=Ticket.STATUS_VALID)
            ticket.save()
        for i in range(n):
            ticket = Ticket(student_id='Used_' + str(i), unique_id='Used_' + str(i), activity_id=published_activity.id,
                            status=Ticket.STATUS_USED)
            ticket.save()
        for i in range(n):
            ticket = Ticket(student_id='Canceled_' + str(i), unique_id='Canceled_' + str(i), activity_id=published_activity.id,
                            status=Ticket.STATUS_CANCELLED)
            ticket.save()

        published_activity.remain_tickets -= 3 * n
        published_activity.save()

        current_time = timezone.now()
        delta_1 = timezone.timedelta(hours=1)
        delta_2 = timezone.timedelta(hours=2)
        delta_3 = timezone.timedelta(days=1)

        book_started_act = Activity(id=4,
                                    name='book_start',
                                    key='key',
                                    place='place',
                                    description='description',
                                    start_time=current_time+delta_3,
                                    pic_url="pic_url",
                                    end_time=current_time+delta_1+delta_3,
                                    book_start=current_time-delta_1,
                                    book_end=current_time+delta_1,
                                    total_tickets=100,
                                    status=Activity.STATUS_PUBLISHED,
                                    remain_tickets=100)
        book_started_act.save()

        started_act = Activity(id=5,
                               name='started',
                               key='key',
                               place='place',
                               description='description',
                               start_time=current_time-delta_1,
                               pic_url="pic_url",
                               end_time=current_time+delta_1,
                               book_start=current_time-delta_3-delta_1,
                               book_end=current_time-delta_3,
                               total_tickets=100,
                               status=Activity.STATUS_PUBLISHED,
                               remain_tickets=100)
        started_act.save()

        ended_act = Activity(id=6,
                             name='ended',
                             key='key',
                             place='place',
                             description='description',
                             start_time=current_time-delta_2,
                             pic_url="pic_url",
                             end_time=current_time-delta_1,
                             book_start=current_time-delta_3-delta_1,
                             book_end=current_time-delta_3,
                             total_tickets=100,
                             status=Activity.STATUS_PUBLISHED,
                             remain_tickets=100)
        ended_act.save()

    def test_get_detail(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        for i in range(1, 4):
            response = c.get('/api/a/activity/detail', {'id':i})
            response_str = response.content.decode('utf-8')
            response_dict = json.loads(response_str)
            self.assertEqual(response_dict['code'], 0)

    def test_change_detail_1(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.SavedID)
        new_name = 'new_'+activity.name
        new_place = 'new_' + activity.place
        new_description = 'new_'+activity.description
        new_picUrl = 'new_' + activity.pic_url
        new_status = Activity.STATUS_PUBLISHED
        response = c.post('/api/a/activity/detail', {'id':self.SavedID,
                                                     'name':new_name,
                                                     'place':new_place,
                                                     'description':new_description,
                                                     'picUrl':new_picUrl,
                                                     'startTime':activity.start_time,
                                                     'endTime':activity.end_time,
                                                     'bookStart':activity.book_start,
                                                     'bookEnd':activity.book_end,
                                                     'totalTickets':activity.total_tickets,
                                                     'status':new_status})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.SavedID)
        self.assertEqual(activity.name, new_name) # 未发布，可修改名称
        self.assertEqual(activity.place, new_place) # 未发布，可修改地点
        self.assertEqual(activity.description, new_description) # 可修改描述
        self.assertEqual(activity.pic_url, new_picUrl) # 可修改图片url
        self.assertEqual(activity.status, new_status) # 未发布，可修改状态

    def test_change_detail_2(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.PublishedID)
        new_name = 'new_'+activity.name
        new_place = 'new_' + activity.place
        new_description = 'new_'+activity.description
        new_picUrl = 'new_' + activity.pic_url
        new_bookStart = activity.book_start + timezone.timedelta(hours=1)
        new_totalTickets = activity.total_tickets + 50
        new_status = Activity.STATUS_SAVED
        response = c.post('/api/a/activity/detail', {'id':self.PublishedID,
                                                     'name':new_name,
                                                     'place':new_place,
                                                     'description':new_description,
                                                     'picUrl':new_picUrl,
                                                     'startTime':activity.start_time,
                                                     'endTime':activity.end_time,
                                                     'bookStart':new_bookStart,
                                                     'bookEnd':activity.book_end,
                                                     'totalTickets':new_totalTickets,
                                                     'status':new_status})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.PublishedID)
        self.assertNotEqual(activity.name, new_name) # 已发布，不能更改名称
        self.assertNotEqual(activity.place, new_place) # 已发布，不能更改地点
        self.assertEqual(activity.description, new_description) # 可更改描述
        self.assertEqual(activity.pic_url, new_picUrl) # 可更改图片url
        self.assertNotEqual(activity.book_start, new_bookStart) # 已发布，不可更改抢票时间
        self.assertNotEqual(activity.status, new_status) # 已发布，不可更改状态

    def test_change_detail_3(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.EndedID)
        new_name = 'new_'+activity.name
        new_place = 'new_' + activity.place
        new_description = 'new_'+activity.description
        new_picUrl = 'new_' + activity.pic_url
        new_start = activity.start_time + timezone.timedelta(hours=1)
        new_end = activity.end_time + timezone.timedelta(hours=1)
        new_bookStart = activity.book_start + timezone.timedelta(hours=1)
        new_bookEnd = activity.book_end + timezone.timedelta(hours=1)
        new_totalTicket = activity.total_tickets + 50
        new_status = Activity.STATUS_SAVED
        response = c.post('/api/a/activity/detail', {'id':self.BookStartID,
                                                     'name':new_name,
                                                     'place':new_place,
                                                     'description':new_description,
                                                     'picUrl':new_picUrl,
                                                     'startTime':new_start,
                                                     'endTime':new_end,
                                                     'bookStart':new_bookStart,
                                                     'bookEnd':new_bookEnd,
                                                     'totalTickets':new_totalTicket,
                                                     'status':new_status})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.BookStartID)
        self.assertNotEqual(activity.name, new_name) # 已发布，不可更改名称
        self.assertNotEqual(activity.place, new_place) # 已发布，不可更改地点
        self.assertEqual(activity.description, new_description)  # 可更改
        self.assertEqual(activity.pic_url, new_picUrl) # 可更改
        self.assertEqual(activity.start_time, new_start) # 活动未结束，可修改
        self.assertEqual(activity.end_time, new_end) # 活动未结束，可修改
        self.assertNotEqual(activity.book_start, new_bookStart) # 已发布，不可修改抢票时间
        self.assertEqual(activity.book_end, new_bookEnd) # 活动未开始，可修改抢票结束时间
        self.assertNotEqual(activity.total_tickets, new_totalTicket) # 抢票已开始，不可修改总票数
        self.assertNotEqual(activity.status, new_status) # 活动已发布，不可修改状态

    def test_change_detail_4(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.EndedID)
        new_name = 'new_'+activity.name
        new_place = 'new_' + activity.place
        new_description = 'new_'+activity.description
        new_picUrl = 'new_' + activity.pic_url
        new_start = activity.start_time + timezone.timedelta(hours=1)
        new_end = activity.end_time + timezone.timedelta(hours=1)
        new_bookStart = activity.book_start + timezone.timedelta(hours=1)
        new_bookEnd = activity.book_end + timezone.timedelta(hours=1)
        new_totalTicket = activity.total_tickets + 50
        new_status = Activity.STATUS_SAVED
        response = c.post('/api/a/activity/detail', {'id':self.StartedID,
                                                     'name':new_name,
                                                     'place':new_place,
                                                     'description':new_description,
                                                     'picUrl':new_picUrl,
                                                     'startTime':new_start,
                                                     'endTime':new_end,
                                                     'bookStart':new_bookStart,
                                                     'bookEnd':new_bookEnd,
                                                     'totalTickets':new_totalTicket,
                                                     'status':new_status})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.StartedID)
        self.assertNotEqual(activity.name, new_name) # 活动已发布，不可修改名称
        self.assertNotEqual(activity.place, new_place) # 活动已发布，不可修改地点
        self.assertEqual(activity.description, new_description) # 可修改
        self.assertEqual(activity.pic_url, new_picUrl) # 可修改
        self.assertEqual(activity.start_time, new_start) # 活动未结束，可修改开始时间
        self.assertEqual(activity.end_time, new_end) # 活动未结束，可修改结束时间
        self.assertNotEqual(activity.book_start, new_bookStart) # 已发布，不可修改抢票时间
        self.assertNotEqual(activity.book_end, new_bookEnd) # 活动已开始，不可修改抢票结束时间
        self.assertNotEqual(activity.total_tickets, new_totalTicket) # 抢票已开始，不可修改总票数
        self.assertNotEqual(activity.status, new_status) # 活动已发布，不可修改状态

    def test_change_detail_5(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.EndedID)
        new_name = 'new_'+activity.name
        new_place = 'new_' + activity.place
        new_description = 'new_'+activity.description
        new_picUrl = 'new_' + activity.pic_url
        new_start = activity.start_time + timezone.timedelta(hours=1)
        new_end = activity.end_time + timezone.timedelta(hours=1)
        new_bookStart = activity.book_start + timezone.timedelta(hours=1)
        new_bookEnd = activity.book_end + timezone.timedelta(hours=1)
        new_totalTicket = activity.total_tickets + 50
        new_status = Activity.STATUS_SAVED
        response = c.post('/api/a/activity/detail', {'id':self.EndedID,
                                                     'name':new_name,
                                                     'place':new_place,
                                                     'description':new_description,
                                                     'picUrl':new_picUrl,
                                                     'startTime':new_start,
                                                     'endTime':new_end,
                                                     'bookStart':new_bookStart,
                                                     'bookEnd':new_bookEnd,
                                                     'totalTickets':new_totalTicket,
                                                     'status':new_status})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        activity = Activity.objects.get(id=self.EndedID)
        self.assertNotEqual(activity.name, new_name)
        self.assertNotEqual(activity.place, new_place)
        self.assertEqual(activity.description, new_description)
        self.assertEqual(activity.pic_url, new_picUrl)
        self.assertNotEqual(activity.start_time, new_start) # 活动已结束，不可修改开始时间
        self.assertNotEqual(activity.end_time, new_end) # 活动已结束，不可修改结束时间
        self.assertNotEqual(activity.book_start, new_bookStart)
        self.assertNotEqual(activity.book_end, new_bookEnd)
        self.assertNotEqual(activity.total_tickets, new_totalTicket)
        self.assertNotEqual(activity.status, new_status)


# class ActivityMenuTest(TestCase):
#     # TODO:
#     # 1.上传菜单按钮
#     # 2.上传菜单按钮后获取菜单按钮
#
#     def setUp(self):
#         User.objects.create_user(userForTest['username'],
#                                  userForTest['email'],
#                                  userForTest['password'])
#
#         current_time = timezone.now()
#         delta_1 = timezone.timedelta(hours=1)
#         delta_2 = timezone.timedelta(days=1)
#
#         for i in range(1, 11):
#             valid_activity = Activity(id=i, name='published' + str(i), key='key', place='place',
#                                       description='description',
#                                       start_time=current_time + delta_2,
#                                       pic_url="pic_url",
#                                       end_time=current_time + delta_2 + delta_1,
#                                       book_start=current_time - delta_1,
#                                       book_end=current_time + delta_1,
#                                       total_tickets=100, status=Activity.STATUS_PUBLISHED, remain_tickets=100)
#             valid_activity.save()
#
#     def test_menu_post(self):
#         c = Client()
#         response = c.post('/api/a/login', userForTest)
#         response_str = response.content.decode('utf-8')
#         response_dict = json.loads(response_str)
#         self.assertEqual(response_dict['code'], 0)
#
#         act_ids = {}
#         acts = Activity.objects.all()
#         for act in acts:
#             act_ids[str(act.id)] = act.id
#         response = c.post('/api/a/activity/menu', act_ids)
#         response_str = response.content.decode('utf-8')
#         response_dict = json.loads(response_str)
#         self.assertEqual(response_dict['code'], 0)
#
#     def test_menu_get(self):
#         time.sleep(2)
#
#         c = Client()
#         response = c.post('/api/a/login', userForTest)
#         response_str = response.content.decode('utf-8')
#         response_dict = json.loads(response_str)
#         self.assertEqual(response_dict['code'], 0)
#
#         response = c.get('/api/a/activity/menu')
#         response_str = response.content.decode('utf-8')
#         response_dict = json.loads(response_str)
#         self.assertEqual(response_dict['code'], 0)
#         for i in range(5):
#             self.assertEqual(response_dict['data'][i]['menuIndex'], i + 1)
#         for i in range(5, 10):
#             self.assertEqual(response_dict['data'][i]['menuIndex'], 0)



class TicketCheckInTest(TestCase):
    # TODO:
    # 1.提交ticket_id并检票成功
    # 2.提交ticket_id并验票失败（票不存在）
    # 3.提交ticket_id并验票失败（电子票已取消）
    # 4.提交ticket_id并验票失败（电子票已使用）
    # 5.提交ticket_id并检票失败（活动验证失败）
    # 6.提交ticket_id并检票失败（活动已结束）
    # 7.提交student_id并检票成功
    # 8.提交student_id并验票失败（票不存在）
    # 9.提交student_id并验票失败（电子票已取消）
    # 10.提交student_id并验票失败（电子票已使用）
    # 11.提交student_id并检票失败（活动验证失败）
    # 12.提交student_id并检票失败（活动已结束）
    # 13.未登录

    ValidID = 1
    EndedID = 2
    WrongID = 3

    def setUp(self):
        User.objects.create_superuser(adminForTest['username'],
                                      adminForTest['email'],
                                      adminForTest['password'])
        User.objects.create_user(userForTest['username'],
                                 userForTest['email'],
                                 userForTest['password'])

        current_time = timezone.now()
        delta_1 = timezone.timedelta(hours=1)
        delta_2 = timezone.timedelta(days=1)

        valid_activity = Activity(id=self.ValidID, name='published', key='key', place='place',
                                  description='description',
                                  start_time=current_time-delta_1,
                                  pic_url="pic_url",
                                  end_time=current_time+delta_1,
                                  book_start=timezone.now(),
                                  book_end=timezone.now(),
                                  total_tickets=100, status=Activity.STATUS_PUBLISHED, remain_tickets=100)

        ended_activity = Activity(id=self.EndedID, name='published', key='key', place='place',
                                  description='description',
                                  start_time=current_time-delta_2,
                                  pic_url="pic_url",
                                  end_time=current_time-delta_1,
                                  book_start=timezone.now(), book_end=timezone.now(),
                                  total_tickets=100, status=Activity.STATUS_PUBLISHED, remain_tickets=100)

        wrong_activity = Activity(id=self.WrongID, name='published', key='key', place='place',
                                  description='description',
                                  start_time=timezone.make_aware(datetime(2018, 10, 15, 18, 0, 0, 0)),
                                  pic_url="pic_url",
                                  end_time=timezone.make_aware(datetime(2018, 10, 15, 23, 0, 0, 0)),
                                  book_start=timezone.now(),
                                  book_end=timezone.now(),
                                  total_tickets=100, status=Activity.STATUS_PUBLISHED, remain_tickets=100)

        valid_ticket = Ticket(student_id='valid_student_id', unique_id='valid_unique_id', activity_id=valid_activity.id,
                              status=Ticket.STATUS_VALID)
        used_ticket = Ticket(student_id='used_student_id', unique_id='used_unique_id', activity_id=valid_activity.id,
                             status=Ticket.STATUS_USED)
        canceled_ticket = Ticket(student_id='canceled_student_id', unique_id='canceled_unique_id',
                                 activity_id=valid_activity.id, status=Ticket.STATUS_CANCELLED)
        ended_ticket = Ticket(student_id='ended_student_id', unique_id='ended_unique_id',
                              activity_id=ended_activity.id, status=Ticket.STATUS_VALID)

        valid_activity.save()
        ended_activity.save()
        wrong_activity.save()
        valid_ticket.save()
        used_ticket.save()
        canceled_ticket.save()
        ended_ticket.save()

    def test_checkin_1(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'ticket': 'valid_unique_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

    def test_checkin_2(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'ticket': 'notexisted_unique_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 5)

    def test_checkin_3(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'ticket': 'canceled_unique_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 2)

    def test_checkin_4(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'ticket': 'used_unique_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 2)

    def test_checkin_5(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.WrongID, 'ticket': 'valid_unique_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 2)

    def test_checkin_6(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.EndedID, 'ticket': 'ended_unique_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 2)

    def test_checkin_7(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'studentId': 'valid_student_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

    def test_checkin_8(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'studentId': 'notexisted_unique_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 5)

    def test_checkin_9(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'studentId': 'canceled_student_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 2)

    def test_checkin_10(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'studentId': 'used_student_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 2)

    def test_checkin_11(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.WrongID, 'studentId': 'valid_student_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 2)

    def test_checkin_12(self):
        c = Client()
        response = c.post('/api/a/login', userForTest)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.post('/api/a/activity/checkin', {'actId': self.EndedID, 'studentId': 'valid_student_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 2)

    def test_checkin_13(self):
        c = Client()
        response = c.post('/api/a/activity/checkin', {'actId': self.ValidID, 'studentId': 'valid_student_id'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 3)
