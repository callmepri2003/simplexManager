from django.core.management.base import BaseCommand
from stripeInt.services import generateHalfTermlyInvoices

class Command(BaseCommand):
    help = 'Generate half-termly invoices'

    def handle(self, *args, **options):
        generateHalfTermlyInvoices()
        self.stdout.write(self.style.SUCCESS('✅ Half-termly invoices generated successfully'))
