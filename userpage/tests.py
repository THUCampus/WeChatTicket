from django.test import TestCase,Client
from django.utils import timezone
from adminpage.views import activityCheckin,activityCreate,activityDelete,activityDetail,activityList,activityMenu,adminLogin,adminLogout
from codex.baseerror import ValidateError
import json
from wechat.models import Activity,Ticket,User
import datetime
from userpage.views import UserBind, UserActivityDetail, TicketDetail


# Create your tests here.
class bindTest(TestCase):
    def setUp(self):
        User.objects.create(open_id='id1', student_id='2016012072')
        User.objects.create(open_id='id2',student_id='')
        User.objects.create(open_id='id3',student_id='')

    def test_usertest_get(self):
        c = Client()
        response = c.get('/api/u/user/bind/?',{"openid":"id1"})
        self.assertEqual(response.json()['data'],"2016012072")

    def test_usertest_get_none(self):
        c = Client()
        response = c.get('/api/u/user/bind/?',{"openid":"id2"})
        self.assertEqual(response.json()['data'],"")

    def test_usertest_post(self):
        User_bind = UserBind()
        User_bind.input = {
            'openid':'id2',
            'student_id':'2016010000',
            'password':'123456test'
        }
        User_bind.post()
        self.assertEqual(User.get_by_openid('id2').student_id, '2016010000')

    # def test_usertest_post_no_password(self):
    #     User_bind = UserBind()
    #     User_bind.input = {
    #         'openid':'id3',
    #         'student_id':'2016010001'
    #     }
    #     User_bind.post()
    #     self.assertEqual(User.get_by_openid('id3').student_id, '2016010000')

    # def test_usertest_post_wrong_studentid(self):
    #     User_bind = UserBind()
    #     User_bind.input = {
    #         'openid':'id2',
    #         'student_id':'2016010002',
    #         'password':'123456test'
    #     }
    #     User_bind.post()
    #     self.assertEqual(User.get_by_openid('id2').student_id, '2016010000')

class activityTest(TestCase):
    def setUp(self):
        Activity.objects.create(id=1, name='act_deleted', key='key1', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=1, remain_tickets=1000)
        Activity.objects.create(id=2, name='act_saved', key='key2', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=0, remain_tickets=1000)

    
    # def test_usertest1(self):
    #     Activity_Detail = UserActivityDetail()
    #     Activity_Detail.input = {
    #         'id':1
    #     }
    #     activity_test = Activity_Detail.get()
    #     self.assertEqual(activity_test.name,"act_deleted")

    # def test_usertest2(self):
    #     Activity_Detail = UserActivityDetail()
    #     Activity_Detail.input = {
    #         'id':2
    #     }
    #     activity_test = Activity_Detail.get()
    #     self.assertNotEqual(activity_test.name,"act_saved")

class detailTest(TestCase):
    def setUp(self):
        act = Activity.objects.create(id=1, name='act_saved', key='key1', place='place',
                                description='description', start_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 8, 0, 0, 0)), pic_url="url",
                                end_time=timezone.make_aware(datetime.datetime(2018, 10, 28, 18, 0, 0, 0)), book_start=timezone.now(), book_end=timezone.make_aware(datetime.datetime(2018, 10, 27, 18, 0, 0, 0)),
                                total_tickets=1000, status=1, remain_tickets=1000)
        User.objects.create(open_id='id1',student_id='2016012072')
        User.objects.create(open_id='id2',student_id='2016012000')
        User.objects.create(open_id='id3',student_id='2016012001')
        Ticket.objects.create(student_id="2016012072",unique_id='1',activity=act, status=1)

    # def test_usertest1(self):
    #     Ticket_Detail = TicketDetail()
    #     Ticket_Detail.input = {
    #         'openid':'id1',
    #         'ticket':'1'
    #     }
    #     ticket_test = Ticket_Detail.get()
    #     self.assertEqual(ticket_test.activityName,"act_saved")

    # def test_usertest2(self):
    #     res = self.client.get('/api/u/ticket/detail/', {'openid' : 'id1'})
    #     self.assertNotEqual(res.json()['code'],0)

    # def test_usertest3(self):
    #     res = self.client.get('/api/u/ticket/detail/', {'student_id':'2016012072'})
    #     self.assertNotEqual(res.json()['code'],0)

    # def test_usertest4(self):
    #     res = self.client.get('/api/u/ticket/detail/', {'openid' : 'id2','student_id':'2016012000'})
    #     self.assertNotEqual(res.json()['code'],0)

    # def test_usertest5(self):
    #     res = self.client.get('/api/u/ticket/detail/', {'openid' : 'id3','student_id':'2016012001'})
    #     self.assertNotEqual(res.json()['code'],0)

