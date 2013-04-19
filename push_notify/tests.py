from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from datetime import datetime
import types

from models import MobileDevice, PushMessage

@override_settings(NOTIFY_BADGE=None)
class PushMesageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'testuser@test.com', 'pw')
        token = '6F39E0E8BDED48269D5C3C55D43A6032A75F8D1AF0EE4A6E9F7516B40C6250EA'
        self.device = MobileDevice(user=self.user, devicetoken=token)
        self.device.save()
        self.old_get_connection = MobileDevice.get_push_service_connection

        @classmethod
        def mock_get_connection(cls):
            class MockSocket(object):
                 def send(self, msg):
                     pass

                 def close(self):
                     pass

            return MockSocket()

        MobileDevice.get_push_service_connection = mock_get_connection

    def tearDown(self):
        MobileDevice.get_push_service_connection = self.old_get_connection

    def test_message_creation(self):
        PushMessage.queue_message(self.user, 'hi')
        self.assertTrue(PushMessage.objects.all().count() > 0)

    def test_message_sent(self):
        PushMessage.queue_message(self.user, 'hi')
        unsent = PushMessage.objects.filter(sent=False).count()
        self.assertEqual(1, unsent)

        PushMessage.send_pending_messages()

        unsent = PushMessage.objects.filter(sent=False).count()
        self.assertEqual(0, unsent)

    def test_adding_data_dict(self):
        PushMessage.queue_message(self.user, 'hi', data={'key': 'value'})
        self.assertTrue(PushMessage.objects.all().count() > 0)

        PushMessage.send_pending_messages()

        unsent = PushMessage.objects.filter(sent=False).count()
        self.assertEqual(0, unsent)

    def test_adding_data_str(self):
        PushMessage.queue_message(self.user, 'hi', data="string")
        self.assertTrue(PushMessage.objects.all().count() > 0)

        PushMessage.send_pending_messages()

        unsent = PushMessage.objects.filter(sent=False).count()
        self.assertEqual(0, unsent)

    def test_custom_badge_counter(self):
        self.msg_str = ''

        @classmethod
        def mock_get_connection(cls):
            class MockSocket(object):
                 def send(mockself, msg):
                     self.msg_str = str(msg)

                 def close(mockself):
                     pass

            return MockSocket()

        MobileDevice.get_push_service_connection = mock_get_connection
        PushMessage.queue_message(self.user, 'hi')
        with override_settings(NOTIFY_BADGE='notify.tests.MockBadgeCounter'):
            PushMessage.send_pending_messages()

        self.assertTrue(0 < self.msg_str.find('badge":42'))

    def test_future_schedule(self):
        future = datetime.max.replace(tzinfo=timezone.utc)
        PushMessage.queue_message(self.user, 'hi', readytime=future)
        self.assertTrue(PushMessage.objects.filter(sent=False).count() > 0)
        send_count = PushMessage.send_pending_messages()
        self.assertEqual(0, send_count)
        self.assertTrue(PushMessage.objects.filter(sent=False).count() > 0)

    def test_no_msg_no_connection(self):
        """
        Verifies that a socket is not opened if there are no messages to send
        """
        self.sock_created = False
        @classmethod
        def mock_get_connection(cls):
            class MockSocket(object):
                def __init__(other): self.sock_created = True
                def send(other, msg): return None
                def close(other): return None

            return MockSocket()

        MobileDevice.get_push_service_connection = mock_get_connection
        call_command('send_push_notifications')

        self.assertFalse(self.sock_created)


class MockBadgeCounter(object):
    def badge(self, user):
        return 42

