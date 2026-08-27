from django.core.management.base import BaseCommand

from devotionals.services import send_todays_devotional_push


class Command(BaseCommand):
    help = "Sends today's devotional as an FCM push to all registered devices. Intended to run once a day via cron."

    def handle(self, *args, **options):
        result = send_todays_devotional_push()
        self.stdout.write(self.style.SUCCESS(result))
