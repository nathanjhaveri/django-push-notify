from django.core.management.base import BaseCommand, CommandError
from notify.models import MobileDevice

class Command(BaseCommand):
    help = 'Contacts the apple push notification feedback service to get list of expired device ids'

    def handle(self, *args, **options):
        count = MobileDevice.remove_expired()
        self.stdout.write('Disabled {0} devices\n'.format(count))

