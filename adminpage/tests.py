import json
from django.utils import timezone
import copy
from django.test import Client, TestCase
from django.contrib.auth.models import User
from wechat.models import Activity, Ticket
from codex.baseerror import *
from adminpage.views.admin import *
from adminpage.views.activity import *

adminForTest = {"username": "admin", "email": "admin@test.com", "password": "admin_psw"}
userForTest = {"username": "user", "email": "user@test.com", "password": "user_psw"}
wrongUserForTest = {"username": "user", "email": "user@test.com", "password": "user_wrong_psw"}
admin_tuple = (adminForTest['username'], adminForTest['email'], adminForTest['password'])
user_tuple = (userForTest['username'], userForTest['email'], userForTest['password'])
admin_json = json.dumps(adminForTest)
user_json = json.dumps(userForTest)

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


class GetLoginStatusTest(TestCase):
    "test getting login status"
    def setUp(self):
        User.objects.create_superuser(admin_tuple)
        User.objects.create_user(user_tuple)

    def tearDown(self):
        pass

    def test_not_login(self):
        c = Client()
        response = c.get('/api/a/login')
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 1)

    def test_already_login(self):
        c = Client()
        c.post('/api/a/login', user_json)
        response = c.get('/api/a/login')
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)


class LoginTest(TestCase):
    "test logging in"
    def setUp(self):
        User.objects.create_superuser(admin_tuple)
        User.objects.create_user(user_tuple)

    def tearDown(self):
        pass

    def test_admin_login(self):
        c = Client()
        response = c.post('/api/a/login', admin_json)
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

    def test_user_login(self):
        c = Client()
        response = c.post('/api/a/login', user_json)
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
        User.objects.create_superuser(admin_tuple)
        User.objects.create_user(user_tuple)

    def tearDown(self):
        pass

    def test_user_logout(self):
        c = Client()
        c.post('/api/a/login', user_json)
        response = c.post('/api/a/logout')
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)


class ActivityDeleteTest(TestCase):

    def setUp(self):
        deleted_activity.save()
        saved_activity.save()
        published_activity.save()

    def tearDown(self):
        Activity.objects.get(id=1).delete()
        Activity.objects.get(id=2).delete()
        Activity.objects.get(id=3).delete()

    def test_activity_list(self):
        c = Client()
        c.post('/api/a/login', admin_json)
        response = c.post('/api/a/activity/list')
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        response_list = response_dict['data']
        self.assertEqual(len(response_list), 2)

    def test_activity_delete_success(self):
        c = Client()
        c.post('/api/a/login', admin_json)
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
        pass

    def tearDown(self):
        pass

    def test_activity_create(self):
        c = Client()
        c.post('/api/a/login', admin_json)
        response = c.post('/api/a/activity/create', json.dumps(published_activity))
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)