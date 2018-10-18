from django.test import TestCase, Client
from wechat.models import User, Activity
import json
from django.utils import timezone
import xml.etree.ElementTree as ET
from datetime import timedelta

test_user_openid = ['1111', '2222']
test_student_id = [2016018485, 2016016666]

ticket_unique_id = 'fff'

XML_TEXT_BASE = """
<xml>
 <ToUserName><![CDATA[aaabbb]]></ToUserName>
 <FromUserName><![CDATA[%s]]></FromUserName>
 <CreateTime>1460536575</CreateTime>
 <MsgType>text</MsgType>
 <MsgId>6272956824639273066</MsgId>
 <Content><![CDATA[%s]]></Content>
</xml>"""

reply_data = '<![CDATA[%s]]>'

published_activity = Activity(id=3, name='published', key='key', place='place',
                              description='description', start_time=timezone.now() + timedelta(666), pic_url="pic_url",
                              end_time=timezone.now() + timedelta(999), book_start=timezone.now() + timedelta(-6), book_end=timezone.now() + timedelta(9),
                              total_tickets=1, status=Activity.STATUS_PUBLISHED, remain_tickets=1)

published_activity2 = Activity(id=1, name='published2', key='key2', place='place',
                              description='description', start_time=timezone.now() + timedelta(666), pic_url="pic_url",
                              end_time=timezone.now() + timedelta(999), book_start=timezone.now() + timedelta(-6), book_end=timezone.now() + timedelta(9),
                               total_tickets=1000, status=Activity.STATUS_PUBLISHED, remain_tickets=1000)

class TicketOperationTestCase(TestCase):
    """
    Test user bind
    """
    def setUp(self):
        # if you visit in wechat, will do the following things
        user_len = len(test_user_openid)
        for i in range(user_len):
            User(open_id=test_user_openid[i], student_id=test_student_id[i]).save()
        self.c = Client()
        published_activity.save()
        published_activity2.save()
        self.get_key_text = [XML_TEXT_BASE % (test_user_openid[i], '抢票 key') for i in range(user_len)]
        self.get_key_text2 = [XML_TEXT_BASE % (test_user_openid[i], '抢票 key2') for i in range(user_len)]
        self.refund_key_text = [XML_TEXT_BASE % (test_user_openid[i], '退票 key') for i in range(user_len)]
        self.show_key_text = [XML_TEXT_BASE % (test_user_openid[i], '取票 key') for i in range(user_len)]

    def tearDown(self):
        for i in range(len(test_user_openid)):
            User.objects.get(open_id=test_user_openid[i]).delete()
        # Activity.objects.get(id=3).delete()
        # Activity.objects.get(id=1).delete()

    def test_ticket(self):
        def test_get(send_data, result, start_with=False):
            response = self.c.post('/wechat', send_data, content_type='application/xml')
            response_str = response.content.decode('utf-8')
            root = ET.fromstring(response_str)
            if not start_with:
                self.assertEqual(root.find('Content').text, result)
            else:
                self.assertTrue(root.find('Content').text.startswith(result))

        # 自己没有抢票的时候退票取票
        test_get(self.refund_key_text[0], '不存在未使用的票')
        test_get(self.show_key_text[0], '不存在未使用的票')
        # 正常抢票
        test_get(self.get_key_text[0], '抢票成功')
        # 没有票的时候第二个人抢票
        test_get(self.get_key_text[1], '抢票失败')
        # 正常抢票
        test_get(self.get_key_text2[0], '抢票成功')
        # 正常抢票
        test_get(self.get_key_text2[1], '抢票成功')
        # 第二次抢票
        test_get(self.get_key_text2[0], '已经抢过票了')
        # 正常退票
        test_get(self.refund_key_text[0], '退票成功')

        # 测试退票后仍然正常
        # 自己没有抢票的时候退票取票
        test_get(self.refund_key_text[0], '不存在未使用的票')
        test_get(self.show_key_text[0], '不存在未使用的票')
        # 正常抢票
        test_get(self.get_key_text[0], '抢票成功')
        # 没有票的时候第二个人抢票
        test_get(self.get_key_text[1], '抢票失败')
        # 第二次抢票
        test_get(self.get_key_text2[0], '已经抢过票了')
        # 正常退票
        test_get(self.refund_key_text[0], '退票成功')
        # 第二个人抢票
        test_get(self.get_key_text[1], '抢票成功')
