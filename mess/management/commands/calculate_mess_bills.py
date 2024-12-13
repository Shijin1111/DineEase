from django.core.management.base import BaseCommand
from mess.views import calculate_mess_bills

class Command(BaseCommand):
    help = 'Calculate mess bills for the current month'

    def handle(self, *args, **kwargs):
        try:
            calculate_mess_bills()
            self.stdout.write(self.style.SUCCESS('Mess bills calculated successfully'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
