from django.core.management.base import NoArgsCommand
from mailer.engine import retry_deferred


class Command(NoArgsCommand):
    help = 'Attempt to resend any deferred mail.'

    def handle_noargs(self, **options):
        retry_deferred()
