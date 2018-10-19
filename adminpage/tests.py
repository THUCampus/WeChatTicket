from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User
from adminpage.views import adminLogin, adminLogout, activityCheckin, activityCreate, activityDelete, activityDetail, activityList, activityMenu
from codex.baseerror import ValidateError
import json
import datetime
from wechat.models import Activity, Ticket

# Create your tests here.

#登录
class adminLoginTest(TestCase):
    #初始化
    def setUp(self):
        User.objects.create_superuser('superuser', 'superuser@test.com', '123456test')
        User.objects.create_user('user', 'user@test.com', '123456test')

    #路由测试
    def test_login_url(self):
        c = Client()
        response = c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        self.assertEqual(response.status_code, 200)
    
    #superuser登录测试
    def test_superuser(self):
        c = Client()
        response = c.post('/api/a/login', {"username": "superuser", "password": "123456test"})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    #user登录测试
    def test_user(self):
        c = Client()
        response = c.post('/api/a/login', {"username": "user", "password": "123456test"})
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

    #密码错误测试
    def test_pwd_error(self):
        a_login = adminLogin()
        a_login.input = {
            'username':'superuser',
            'password':'test123456'
        }
        self.assertRaises(ValidateError, a_login.post)

    #用户名无效测试
    def test_username_not_exit(self):
        a_login = adminLogin()
        a_login.input = {
            'username':'null_user',
            'password':'123456test'
        }
        self.assertRaises(ValidateError, a_login.post)

#登出
class adminLogoutTest(TestCase):
    #登出测试
    def logoutTest(self):
        c = Client()
        response = c.post('/api/a/logout', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode())['code'], 0)

#活动列表
class activityListTest(TestCase):
    #初始化
    def setUp(self):
        Activity.objects.create(id=1, name='act_deleted', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_DELETED, remain_tickets=1000)
        Activity.objects.create(id=2, name='act_saved', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_SAVED, remain_tickets=1000)
        Activity.objects.create(id=3, name='act_published', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)
    
    #get测试
    def test_get_act_List(self):
        A = activityList()
        get = A.get()
        self.assertEqual(len(get), 2)
    
    #回退
    def tearDown(self):
        Activity.objects.all().delete()

#创建活动
class create_act_Test(TestCase):
    #post测试
    def test_create_act(self):
        act = {"name": "name", "key": "key", "place": "place", "description": "description", "picUrl": "picUrl",
                     "startTime": timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), 
                     "endTime": timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)),
                     "bookStart": timezone.now(), "bookEnd": timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)), 
                     "totalTickets": 1000, "status": Activity.STATUS_PUBLISHED}
        A = activityCreate()
        A.input = act
        A.post()
        self.assertEqual(Activity.objects.get(name='name').place, "place")

    #回退
    def clear(self):
        Activity.objects.all().delete()

#删除活动
class delete_act_Test(TestCase):
    #初始化
    def setUp(self):
        Activity.objects.create(id=1, name='act_deleted', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_DELETED, remain_tickets=1000)
        Activity.objects.create(id=2, name='act_saved', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_SAVED, remain_tickets=1000)
        Activity.objects.create(id=3, name='act_published', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)

    #post测试
    #删除存在的活动
    def test_delete_act_exited(self):
        A_delete = activityDelete()
        A_delete.input = {'id': 2}
        A_delete.post()
        self.assertEqual(Activity.objects.get(id=2).status, Activity.STATUS_DELETED)
    #删除已删除的活动
    def test_delete_act_deleted(self):
        A_delete = activityDelete()
        A_delete.input = {'id': 1}    
        self.assertRaises(ValidateError, A_delete.post)
    #删除不存在的活动
    def test_delete_act_not_exited(self):
        A_delete = activityDelete()
        A_delete.input = {'id': 4}    
        self.assertRaises(ValidateError, A_delete.post)
    
    #回退
    def tearDown(self):
        Activity.objects.all().delete()

#活动详情
class act_details_Test(TestCase):
    #初始化
    def setUp(self):
        Activity.objects.create(id=1, name='act_saved', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_SAVED, remain_tickets=1000)
    
    #获取存在的活动
    def test_get_details_act_exited(self):
        act_detail = activityDetail()
        act_detail.input = {'id': 1}
        self.assertEqual(act_detail.get()['name'], "act_saved")

    #获取不存在的活动
    def test_get_details_act_not_exited(self):
        act_detail = activityDetail()
        act_detail.input = {'id': 2}
        self.assertRaises(ValidateError, act_detail.get)

    #回退
    def tearDown(self):
        Activity.objects.all().delete()

#微信菜单调整
class act_Menu_Test(TestCase):
    #初始化
    def setUp(self):
        Activity.objects.create(id=1, name='act_deleted', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_DELETED, remain_tickets=1000)
        Activity.objects.create(id=2, name='act_saved', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_SAVED, remain_tickets=1000)
        Activity.objects.create(id=3, name='act_published', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)

    #获取菜单测试
    # def test_get_menu_test(self):
    #     menu = activityMenu()
    #     act_list = menu.get()
    #     self.assertEqual(len(act_list), 1)
    #     self.assertEqual(act_list[0]['name'], 'act_published')

    #修改菜单测试
    def test_post_menu_test(self):
        menu = activityMenu()
        menu.input = {'id':2}
        self.assertRaises(ValidateError, menu.post)
    
    #回退
    def tearDown(self):
        Activity.objects.all().delete()

#检票
class activity_checkin_Test(TestCase):
    #初始化
    def setUp(self):
        act = Activity.objects.create(id=1, name='act_published', key='key', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)
        Ticket.objects.create(student_id = '1', unique_id='1', activity= act, status=Ticket.STATUS_CANCELLED)
        Ticket.objects.create(student_id = '2', unique_id='2', activity= act, status=Ticket.STATUS_USED)
        Ticket.objects.create(student_id = '3', unique_id='3', activity= act, status=Ticket.STATUS_VALID)

    #正常检票
    def test_checkin_vaild1(self):
        C = activityCheckin()
        C.input = {'actId':1, 'studentId':'3'}
        info = C.post()
        self.assertEqual(info['ticket'], '3')

    def test_checkin_vaild2(self):
        C = activityCheckin()
        C.input = {'actId':1, 'ticket':'3'}
        info = C.post()
        self.assertEqual(info['ticket'], '3')

    #已用票检票
    def test_checkin_used1(self):
        C = activityCheckin()
        C.input = {'actId':1, 'studentId':'2'}
        self.assertRaises(ValidateError, C.post)

    def test_checkin_used2(self):
        C = activityCheckin()
        C.input = {'actId':1, 'ticket':'2'}
        self.assertRaises(ValidateError, C.post)

    #退票检票
    def test_checkin_invaild1(self):
        C = activityCheckin()
        C.input = {'actId':1, 'studentId':'1'}
        self.assertRaises(ValidateError, C.post)

    def test_checkin_invaild2(self):
        C = activityCheckin()
        C.input = {'actId':1, 'ticket':'1'}
        self.assertRaises(ValidateError, C.post)

    #回退
    def tearDown(self):
        Ticket.objects.all().delete()
        Activity.objects.all().delete()