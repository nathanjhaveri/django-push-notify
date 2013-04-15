from django.core.management.base import BaseCommand, CommandError
from notify.models import PushMessage

class Command(BaseCommand):
    help = 'Sends pending push notifications'

    def handle(self, *args, **options):
        self.stdout.write('sending pending notifications\n')
        msg_count = PushMessage.send_pending_messages()
        self.stdout.write('sent {0} messages\n'.format(msg_count))

