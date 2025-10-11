from django.core.management.base import BaseCommand
from stripeInt.services import generateTermlyInvoices

class Command(BaseCommand):
    help = 'Generate termly invoices'

    def handle(self, *args, **options):
        generateTermlyInvoices()
        self.stdout.write(self.style.SUCCESS('✅ Termly invoices generated successfully'))
