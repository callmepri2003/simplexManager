import logging
import re
import subprocess
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time
from django.conf import settings
from django.test import Client, TestCase
import requests
import stripe
import os
from dotenv import load_dotenv
import uuid

from stripeInt.models import StripeProd
from tutoring.models import BasketItem, Parent
from .services import generateInvoices

load_dotenv()

class ServicesTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
      super().setUpClass()
      stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
      webhook_url = f"{cls.live_server_url}/stripe/webhooks/"
      
      # Test that the server is actually reachable
      import requests
      try:
          response = requests.get(cls.live_server_url)
      except Exception as e:
          print(f"Server test failed: {e}")


      # Create log file
      log_file = open('stripe_cli.log', 'w')

      cls._wait_for_server_ready()

      cls.stripe_process = subprocess.Popen([
          'stripe', 'listen', 
          '--forward-to', webhook_url,
          '--api-key', os.getenv('STRIPE_SECRET_KEY')
      ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
      
      cls.log_file = log_file  # Keep reference to close later
      webhook_secret = None

      time.sleep(3)

      for line in cls.stripe_process.stdout:
        log_file.write(line)  # Write to log file
        log_file.flush()
        print(line.strip())   # Also print to console
        
        # Look for the webhook signing secret
        if "webhook signing secret is" in line:
            match = re.search(r'whsec_[a-zA-Z0-9]+', line)
            if match:
                webhook_secret = match.group(0)
                os.environ['WEBHOOK_SIGNING_SECRET'] = webhook_secret
                break
        
        # Break when we see "Ready!" to avoid blocking
        if "Ready!" in line:
            break

      
      # Wait for server to start
      time.sleep(3)

      cls.client = Client()
      cls.url = "/stripe/webhooks/"
    
    @classmethod
    def tearDownClass(cls):
        # Terminate the Stripe CLI process
        if hasattr(cls, 'stripe_process') and cls.stripe_process:
            cls.stripe_process.terminate()
            # Wait a bit for graceful shutdown
            try:
                cls.stripe_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                cls.stripe_process.kill()
                cls.stripe_process.wait()
        
        # Close the log file
        if hasattr(cls, 'log_file') and cls.log_file:
            cls.log_file.close()
        
        # Call parent cleanup
        super().tearDownClass()
  
    def test_SimpleHappyPath(self):
        '''
        Things that I aim to test
        1.
        Happy path, creating a customer, creating a product with a price or separately
        then invoicing that customer. The invoice details should match the preferences
        '''
        name = uniquify("Jenny Rosen")
        email = uniquify("jennyrosen@example.com")
        product_name = uniquify("Private, In Person")

        self.assertEqual(len(Parent.objects.all()), 0)
        self.assertEqual(len(StripeProd.objects.all()), 0)

        customer = stripe.Customer.create(
        name = name,
        email = email,
        )

        time.sleep(2)

        self.assertEqual(len(Parent.objects.all()), 1)
        self.assertEqual(len(StripeProd.objects.all()), 0)

        product = stripe.Product.create(
            name=product_name,
        )
        
        time.sleep(3)

        stripe.Price.create(
            currency="AUD",
            unit_amount=6000,
            product=product.id,
        )

        time.sleep(3)

        self.assertEqual(len(Parent.objects.all()), 1)
        self.assertEqual(len(StripeProd.objects.all()), 1)

        parent = Parent.objects.get(name=name)
        parent.payment_frequency = 'fortnightly'
        product = StripeProd.objects.get(name=product_name)
        basketItem = BasketItem(
            basket=parent.basket,
            product=product,
            quantity=2
        )
        basketItem.save()
        # TODO: quantity can't always be 2
        parent.save()

        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        invoices = stripe.Invoice.list(limit=10)
        customerFound = False
        for invoice in invoices['data']:
            if(parent.stripeId == invoice['customer']):
                customerFound = True
                amount = invoice['subtotal']
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                self.assertEqual(len(line_items), 1)
                self.assertEqual(line_items[0]['amount'], 24000)
                self.assertEqual(line_items[0]['quantity'], 4)

        self.assertTrue(customerFound)

    def test_invoicingCorrectQuantities(self):
  
        '''
        2.
        Correctly invoicing the correct quantities,
        fortnightly group
        half termly group
        half termly private
        fortnightly group
        etc
        '''
        name1 = uniquify("Jenny Rosen 1")
        email1 = uniquify("jennyrosen1@example.com")
        product_name1 = uniquify("Private, In Person")

        name2 = uniquify("Jenny Rosen 2")
        email2 = uniquify("jennyrosen@example.com")
        product_name2 = uniquify("Group, Year 5-6")

        self.assertEqual(len(Parent.objects.all()), 0)
        self.assertEqual(len(StripeProd.objects.all()), 0)

        customer1 = stripe.Customer.create(
            name = name1,
            email = email2,
        )
        customer2 = stripe.Customer.create(
            name = name2,
            email = email2,
        )

        time.sleep(2)

        self.assertEqual(len(Parent.objects.all()), 2)
        self.assertEqual(len(StripeProd.objects.all()), 0)

        product1 = stripe.Product.create(
            name=product_name1,
        )
        
        time.sleep(3)

        stripe.Price.create(
            currency="AUD",
            unit_amount=6000,
            product=product1.id,
        )

        time.sleep(3)

        self.assertEqual(len(Parent.objects.all()), 2)
        self.assertEqual(len(StripeProd.objects.all()), 1)

        parent1 = Parent.objects.get(name=name1)
        parent2 = Parent.objects.get(name=name2)
        parent1.payment_frequency = 'fortnightly'
        parent2.payment_frequency = 'halftermly'
        parent1.save()
        parent2.save()
        product = StripeProd.objects.get(name=product_name1)
        # same product for both
        basketItem1 = BasketItem(
            basket=parent1.basket,
            product=product,
            quantity=2
        )
        basketItem2 = BasketItem(
            basket=parent2.basket,
            product=product,
            quantity=2
        )
        basketItem1.save()
        basketItem2.save()

        generateInvoices(frequency="fortnightly", amount_of_weeks=2)
        generateInvoices(frequency="halftermly", amount_of_weeks=5)
        generateInvoices(frequency="weekly", amount_of_weeks=1)

        time.sleep(3)

        invoices = stripe.Invoice.list(limit=500)
        parent1Found = False
        parent2Found = False
        with open("invoice_ids.txt", "w") as f:
            while True:
                for invoice in invoices['data']:
                    f.write(invoice['customer'] + "\n")
                    if parent1.stripeId == invoice['customer']:
                        parent1Found = True
                        line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                        self.assertEqual(len(line_items), 1)
                        self.assertEqual(line_items[0]['amount'], 6000 * 2 * 2)  # 60 dollars for 2 hours for 2 weeks
                        self.assertEqual(line_items[0]['quantity'], 4)

                    elif parent2.stripeId == invoice['customer']:
                        parent2Found = True
                        line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                        self.assertEqual(len(line_items), 1)
                        self.assertEqual(line_items[0]['amount'], 6000 * 2 * 5)  # 60 dollars for 2 hours for 5 weeks
                        self.assertEqual(line_items[0]['quantity'], 10)

                    if parent1Found and parent2Found:
                        break

                if parent1Found and parent2Found:
                    break

                if invoices.has_more:
                    invoices = invoices.next_page()
                else:
                    break
        self.assertTrue(parent1Found)
        self.assertTrue(parent2Found)




    def test_gracefulChanges(self):
        '''
        3.
        responds gracefully to:
        - changing prices
        - changing customer details
        - changing customer payment frequencies
        '''
        name = uniquify("John Smith")
        email = uniquify("johnsmith@example.com")
        product_name = uniquify("Group, Year 7-8")

        self.assertEqual(len(Parent.objects.all()), 0)
        self.assertEqual(len(StripeProd.objects.all()), 0)

        # Create customer
        customer = stripe.Customer.create(
            name=name,
            email=email,
        )

        time.sleep(2)

        self.assertEqual(len(Parent.objects.all()), 1)

        # Create product with initial price
        product = stripe.Product.create(
            name=product_name,
        )
        
        time.sleep(3)

        initial_price = stripe.Price.create(
            currency="AUD",
            unit_amount=5000,  # $50 initially
            product=product.id,
        )

        time.sleep(3)

        self.assertEqual(len(StripeProd.objects.all()), 1)

        # Set up parent with initial configuration
        parent = Parent.objects.get(name=name)
        parent.payment_frequency = 'fortnightly'
        parent.save()
        
        stripe_product = StripeProd.objects.get(name=product_name)
        basketItem = BasketItem(
            basket=parent.basket,
            product=stripe_product,
            quantity=3
        )
        basketItem.save()

        # Generate initial invoice
        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(3)

        # Verify initial invoice
        invoices = stripe.Invoice.list(limit=10)
        initial_invoice_found = False
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                initial_invoice_found = True
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                self.assertEqual(len(line_items), 1)
                self.assertEqual(line_items[0]['amount'], 5000 * 3 * 2)  # $50 * 3 hours * 2 weeks
                self.assertEqual(line_items[0]['quantity'], 6)
                break

        self.assertTrue(initial_invoice_found)

        # TEST 1: Change price
        new_price = stripe.Price.create(
            currency="AUD",
            unit_amount=6500,  # $65 new price
            product=product.id,
        )

        time.sleep(3)
        
        # Generate invoice after price change
        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(3)

        # Verify new price is reflected
        invoices = stripe.Invoice.list(limit=20)
        price_change_invoice_found = False
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                if len(line_items) > 0 and line_items[0]['amount'] == 6500 * 3 * 2:
                    price_change_invoice_found = True
                    self.assertEqual(line_items[0]['amount'], 6500 * 3 * 2)  # $65 * 3 hours * 2 weeks
                    self.assertEqual(line_items[0]['quantity'], 6)
                    break

        self.assertTrue(price_change_invoice_found)

        # TEST 2: Change customer details
        updated_name = uniquify("John Smith Updated")
        updated_email = uniquify("johnsmith.updated@example.com")
        
        stripe.Customer.modify(
            customer.id,
            name=updated_name,
            email=updated_email,
        )

        time.sleep(3)

        # Generate invoice after customer update
        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(3)

        # Verify invoice still works with updated customer
        invoices = stripe.Invoice.list(limit=30)
        customer_update_invoice_found = False
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                customer_update_invoice_found = True
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                self.assertEqual(len(line_items), 1)
                break

        self.assertTrue(customer_update_invoice_found)

        # TEST 3: Change payment frequency
        original_frequency = parent.payment_frequency
        parent.payment_frequency = 'halftermly'
        parent.save()

        # Generate invoice with new frequency
        generateInvoices(frequency='halftermly', amount_of_weeks=5)

        time.sleep(3)

        # Verify correct quantity for new frequency
        invoices = stripe.Invoice.list(limit=40)
        frequency_change_invoice_found = False
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                # Look for the halftermly invoice (5 weeks worth)
                if len(line_items) > 0 and line_items[0]['quantity'] == 15:  # 3 hours * 5 weeks
                    frequency_change_invoice_found = True
                    self.assertEqual(line_items[0]['amount'], 6500 * 3 * 5)  # $65 * 3 hours * 5 weeks
                    self.assertEqual(line_items[0]['quantity'], 15)
                    break

        self.assertTrue(frequency_change_invoice_found)

        # TEST 4: Change back to original frequency and verify it still works
        parent.payment_frequency = original_frequency
        parent.save()

        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(3)

        # Verify we can change back successfully
        invoices = stripe.Invoice.list(limit=50)
        back_to_original_invoice_found = False
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                # Look for the fortnightly invoice (2 weeks worth)
                if len(line_items) > 0 and line_items[0]['quantity'] == 6:  # 3 hours * 2 weeks
                    back_to_original_invoice_found = True
                    self.assertEqual(line_items[0]['amount'], 6500 * 3 * 2)  # $65 * 3 hours * 2 weeks
                    self.assertEqual(line_items[0]['quantity'], 6)
                    break

        self.assertTrue(back_to_original_invoice_found)

        # TEST 5: Change quantity in basket
        basketItem.quantity = 1  # Change from 3 to 1
        basketItem.save()

        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(3)

        # Verify quantity change is reflected
        invoices = stripe.Invoice.list(limit=60)
        quantity_change_invoice_found = False
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                # Look for the invoice with new quantity (1 hour * 2 weeks)
                if len(line_items) > 0 and line_items[0]['quantity'] == 2:
                    quantity_change_invoice_found = True
                    self.assertEqual(line_items[0]['amount'], 6500 * 1 * 2)  # $65 * 1 hour * 2 weeks
                    self.assertEqual(line_items[0]['quantity'], 2)
                    break

        self.assertTrue(quantity_change_invoice_found)


        '''
        4.
        handles errors gracefully
        - trying to invoice inactive products
        - trying to invoice inactive parents
        - what else
        '''

        '''
        5.
        Make sure it doesn't generate invoices that try to automatically charge them
        Ensure correct metadata
        It should have the same data as is on the google sheets
        '''
    @classmethod
    def _wait_for_server_ready(cls):
        """Wait for the live server to be ready to accept connections"""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{cls.live_server_url}/admin/", timeout=1)
                print(f"Server ready after {attempt + 1} attempts")
                return
            except (requests.ConnectionError, requests.Timeout):
                if attempt == max_attempts - 1:
                    raise Exception("Server failed to start")
                time.sleep(0.5)

def uniquify(targetString):
    return f"{str(uuid.uuid4())[:8]}_{targetString}"