"""
Django management command to send appointment reminders
Usage: python manage.py send_reminders
"""
from django.core.management.base import BaseCommand
from appointments.reminder_utils import send_all_reminders


class Command(BaseCommand):
    help = 'Send appointment reminders for appointments scheduled tomorrow'

    def handle(self, *args, **options):
        """Execute the command"""
        self.stdout.write(self.style.SUCCESS('Starting reminder sending process...'))
        
        result = send_all_reminders()
        
        if result['sent'] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully sent {result['sent']} reminder(s)"
                )
            )
        
        if result['failed'] > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Failed to send {result['failed']} reminder(s)"
                )
            )
        
        if result['total'] == 0:
            self.stdout.write(
                self.style.WARNING('No appointments found that need reminders')
            )
