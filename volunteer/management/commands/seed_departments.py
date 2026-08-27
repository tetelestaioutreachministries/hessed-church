from django.core.management.base import BaseCommand

from volunteer.models import Department

DEPARTMENTS = [
    "Ushering & Security",
    "Kids Church",
    "Music Team",
    "Prayer Team",
    "Administrative Support",
    "Production Design",
    "Technical & Stage Management",
    "Communications",
]


class Command(BaseCommand):
    help = "Seeds the 8 standard volunteer departments (contact_email left blank for staff to fill in via /admin/)."

    def handle(self, *args, **options):
        created_count = 0
        for order, name in enumerate(DEPARTMENTS):
            _, created = Department.objects.get_or_create(name=name, defaults={"order": order})
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created department: {name}"))
            else:
                self.stdout.write(f"Already exists: {name}")

        self.stdout.write(self.style.SUCCESS(f"Done. {created_count} department(s) created."))
