from django.test import TestCase, Client
from wechat.models import User, Activity, Ticket
import json
from django.utils import timezone
from datetime import timedelta

deleted_activity = Activity(id=1, name='deleted', key='key', place='place',
                            description='description', start_time=timezone.now(), pic_url="pic_url",
                            end_time=timezone.now(), book_start=timezone.now(), book_end=timezone.now(),
                            total_tickets=100, status=Activity.STATUS_DELETED, remain_tickets=100)

saved_activity = Activity(id=2, name='saved', key='key', place='place',
                          description='description', start_time=timezone.now(), pic_url="pic_url",
                          end_time=timezone.now(), book_start=timezone.now(), book_end=timezone.now(),
                          total_tickets=100, status=Activity.STATUS_SAVED, remain_tickets=100)

published_activity = Activity(id=3, name='published', key='key', place='place',
                              description='description', start_time=timezone.now() + timedelta(666), pic_url="pic_url",
                              end_time=timezone.now() + timedelta(999), book_start=timezone.now() + timedelta(-6), book_end=timezone.now() + timedelta(9),
                              total_tickets=100, status=Activity.STATUS_PUBLISHED, remain_tickets=100)

test_user_openid = '1111'
test_student_id = 2016018485

ticket_unique_id = 'fff'

class UserBindTestCase(TestCase):
    """
    Test user bind
    """
    def setUp(self):
        # if you visit in wechat, will do the following things
        User.objects.get_or_create(open_id=test_user_openid)

    def tearDown(self):
        User.objects.get(open_id=test_user_openid).delete()

    def test_bind(self):
        c = Client()
        response = c.get('/api/u/user/bind', {'openid': test_user_openid})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['data'], '')

        response = c.post('/api/u/user/bind', {'openid': test_user_openid, 'student_id': test_student_id, 'password': 'hhh'})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)

        response = c.get('/api/u/user/bind', {'openid': test_user_openid})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['data'], str(test_student_id))


class ActivityGetTestCase(TestCase):
    """
    Test activity get
    """
    def setUp(self):
        deleted_activity.save()
        saved_activity.save()
        published_activity.save()

    def tearDown(self):
        Activity.objects.get(id=1).delete()
        Activity.objects.get(id=2).delete()
        Activity.objects.get(id=3).delete()

    def test_notavailable_activity_get(self):
        c = Client()
        response = c.get('/api/u/activity/detail', {'id': 1})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertNotEqual(response_dict['code'], 0)

        response = c.get('/api/u/activity/detail', {'id': 2})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertNotEqual(response_dict['code'], 0)

        response = c.get('/api/u/activity/detail', {'id': 666})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertNotEqual(response_dict['code'], 0)

    def test_activity_get(self):
        c = Client()
        response = c.get('/api/u/activity/detail', {'id': 3})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)
        response_dict = response_dict['data']
        self.assertEqual(response_dict['name'], 'published')
        self.assertEqual(response_dict['bookStart'], int(published_activity.book_start.timestamp()))


class TicketGetTestCase(TestCase):
    """
    Test activity get
    """
    def setUp(self):
        User.objects.get_or_create(open_id=test_user_openid)
        published_activity.save()
        ticket_test = Ticket(student_id=test_student_id, unique_id=ticket_unique_id, activity_id=published_activity.id, status=Ticket.STATUS_VALID)
        ticket_test.save()

    def tearDown(self):
        User.objects.get(open_id=test_user_openid).delete()
        Ticket.objects.get(unique_id=ticket_unique_id).delete()
        Activity.objects.get(id=3).delete()

    def test_ticket_get(self):
        c = Client()
        c.post('/api/u/user/bind', {'openid': test_user_openid, 'student_id': test_student_id, 'password': 'hhh'})
        response = c.get('/api/u/ticket/detail', {'ticket': ticket_unique_id, 'openid': test_user_openid})
        response_str = response.content.decode('utf-8')
        response_dict = json.loads(response_str)
        self.assertEqual(response_dict['code'], 0)
        response_dict = response_dict['data']
        self.assertEqual(response_dict['activityName'], 'published')
        self.assertEqual(response_dict['startTime'], int(published_activity.start_time.timestamp()))
        self.assertEqual(response_dict['uniqueId'], ticket_unique_id)
