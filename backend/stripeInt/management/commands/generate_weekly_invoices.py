from django.core.management.base import BaseCommand
from stripeInt.services import generateWeeklyInvoices

class Command(BaseCommand):
    help = 'Generate weekly invoices'

    def handle(self, *args, **options):
        generateWeeklyInvoices()
        self.stdout.write(self.style.SUCCESS('✅ Weekly invoices generated successfully'))
