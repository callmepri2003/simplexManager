from django.core.management.base import BaseCommand
from stripeInt.services import generateFortnightlyInvoices

class Command(BaseCommand):
    help = 'Generate fortnightly invoices'

    def handle(self, *args, **options):
        generateFortnightlyInvoices()
        self.stdout.write(self.style.SUCCESS('✅ Fortnightly invoices generated successfully'))
