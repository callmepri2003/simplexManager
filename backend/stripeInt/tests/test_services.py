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
import time

from stripeInt.models import StripeProd
from django.core.management import call_command
from tutoring.models import Parent, TutoringStudent, Group, Lesson, Attendance, LocalInvoice, TutoringTerm, TutoringWeek, TutoringYear
from stripeInt.services import generateInvoices
import stripe

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
        Things that I aim to test:
        1. Happy path - creating a customer, creating a product with a price,
        scheduling lessons, creating students and attendances, then invoicing.
        The invoice details should match the preferences and attendance data.
        '''
        name = uniquify("Jenny Rosen")
        email = uniquify("jennyrosen@example.com")
        product_name = uniquify("Private, In Person")
        
        self.assertEqual(len(Parent.objects.all()), 0)
        self.assertEqual(len(StripeProd.objects.all()), 0)
        
        # Create Stripe customer
        customer = stripe.Customer.create(
            name=name,
            email=email,
        )
        
        time.sleep(2)
        
        self.assertEqual(len(Parent.objects.all()), 1)
        self.assertEqual(len(StripeProd.objects.all()), 0)
        
        # Create Stripe product and price
        product = stripe.Product.create(
            name=product_name,
        )
        
        time.sleep(3)
        
        stripe.Price.create(
            currency="AUD",
            unit_amount=6000,  # $60 per hour
            product=product.id,
        )
        
        time.sleep(3)
        
        self.assertEqual(len(Parent.objects.all()), 1)
        self.assertEqual(len(StripeProd.objects.all()), 1)
        
        # Get parent and product from database
        parent = Parent.objects.get(name=name)
        parent.payment_frequency = 'fortnightly'
        parent.save()
        
        product_obj = StripeProd.objects.get(name=product_name)
        
        # Create a group with associated product
        group = Group.objects.create(
            tutor="Test Tutor",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day="14:00:00",
            lesson_length=1,  # 1 hour lessons
            associated_product=product_obj
        )
        
        # Create a student
        student = TutoringStudent.objects.create(
            name=uniquify("Test Student"),
            parent=parent,
            active=True
        )
        student.group.add(group)
        
        # Schedule lessons using management command
        call_command('set_term', '2025-10-13')
        
        # Get lessons scheduled for the next 2 weeks (fortnightly period)
        from datetime import datetime, timedelta
        period_start = datetime.now()
        period_end = period_start + timedelta(weeks=2)
        
        lessons = Lesson.objects.filter(
            group=group,
            date__gte=period_start,
            date__lt=period_end
        )
        
        # Verify attendances were created (via signal)
        expected_attendance_count = lessons.count()
        self.assertGreater(expected_attendance_count, 0, "Should have lessons scheduled")
        
        attendances = Attendance.objects.filter(
            tutoringStudent=student,
            lesson__in=lessons
        )
        self.assertEqual(attendances.count(), expected_attendance_count)
        
        # Generate invoices
        generateInvoices(frequency='fortnightly', amount_of_weeks=2)
        
        # Wait for webhooks to process
        time.sleep(3)
        
        # Verify invoice was created
        invoices = stripe.Invoice.list(limit=10)
        customerFound = False
        invoice_id = None
        
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                customerFound = True
                invoice_id = invoice['id']
                
                # Get invoice line items
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                
                # Should have 1 line item (grouped by product)
                self.assertEqual(len(line_items), 1)
                
                # Each attendance is 1 hour, so quantity = number of lessons in 2-week period
                expected_quantity = expected_attendance_count * 1.0  # lesson_length
                self.assertEqual(line_items[0]['quantity'], expected_quantity)
                
                # Amount = $60 * quantity
                expected_amount = 6000 * expected_quantity
                self.assertEqual(line_items[0]['amount'], expected_amount)
                
                # Verify description contains student name
                self.assertIn(student.name, line_items[0]['description'])
                
                break
        
        self.assertTrue(customerFound, "Invoice should be created for the parent")
        
        # Verify LocalInvoice was created via webhook
        local_invoice = LocalInvoice.objects.get(stripeInvoiceId=invoice_id)
        self.assertIsNotNone(local_invoice)
        self.assertEqual(local_invoice.status, 'open')  # Invoice is finalized but not paid yet
        self.assertEqual(local_invoice.customer_stripe_id, parent.stripeId)
        
        # Verify all attendances are linked to the local invoice
        linked_attendances = local_invoice.attendances.all()
        self.assertEqual(linked_attendances.count(), expected_attendance_count)
        
        # Verify each attendance is linked
        for attendance in attendances:
            attendance.refresh_from_db()
            self.assertEqual(attendance.local_invoice, local_invoice)

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
        email2 = uniquify("jennyrosen2@example.com")
        product_name2 = uniquify("Group, Year 5-6")

        self.assertEqual(len(Parent.objects.all()), 0)
        self.assertEqual(len(StripeProd.objects.all()), 0)

        customer1 = stripe.Customer.create(
            name = name1,
            email = email1,
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

        # Create students
        student1 = TutoringStudent.objects.create(
            name=uniquify("Test Student1"),
            parent=Parent.objects.get(name=name1),
            active=True
        )

        student2 = TutoringStudent.objects.create(
            name=uniquify("Test Student2"),
            parent=Parent.objects.get(name=name2),
            active=True
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

        product1 = StripeProd.objects.get(name=product_name1)

        group = Group.objects.create(
            tutor="Test Tutor",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day="14:00:00",
            lesson_length=1,  # 1 hour lessons
            associated_product=product1
        )

        student1.group.add(group)
        student2.group.add(group)

        parent1 = Parent.objects.get(name=name1)
        parent2 = Parent.objects.get(name=name2)
        parent1.payment_frequency = 'fortnightly'
        parent2.payment_frequency = 'halftermly'
        parent1.save()
        parent2.save()

        # Schedule lessons using management command
        call_command('set_term', '2025-10-13')

        generateInvoices(frequency="fortnightly", amount_of_weeks=2)
        generateInvoices(frequency="halftermly", amount_of_weeks=5)
        generateInvoices(frequency="weekly", amount_of_weeks=1)

        time.sleep(5)  # Wait longer for multiple webhooks to process

        invoices = stripe.Invoice.list(limit=500)
        parent1Found = False
        parent2Found = False
        parent1_invoice_id = None
        parent2_invoice_id = None
        
        while True:
            for invoice in invoices['data']:
                if parent1.stripeId == invoice['customer']:
                    parent1Found = True
                    parent1_invoice_id = invoice['id']
                    line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                    self.assertEqual(len(line_items), 1)
                    self.assertEqual(line_items[0]['amount'], 6000 * 1 * 2)  # 60 dollars for 1 hour for 2 weeks
                    self.assertEqual(line_items[0]['quantity'], 2)

                elif parent2.stripeId == invoice['customer']:
                    parent2Found = True
                    parent2_invoice_id = invoice['id']
                    line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                    self.assertEqual(len(line_items), 1)
                    self.assertEqual(line_items[0]['amount'], 6000 * 1 * 5)  # 60 dollars for 1 hour for 5 weeks
                    self.assertEqual(line_items[0]['quantity'], 5)

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
        
        # Verify LocalInvoices were created via webhooks
        local_invoice1 = LocalInvoice.objects.get(stripeInvoiceId=parent1_invoice_id)
        local_invoice2 = LocalInvoice.objects.get(stripeInvoiceId=parent2_invoice_id)
        
        self.assertIsNotNone(local_invoice1)
        self.assertIsNotNone(local_invoice2)
        
        # Verify attendances are linked
        self.assertEqual(local_invoice1.attendances.count(), 2)  # 2 weeks of lessons
        self.assertEqual(local_invoice2.attendances.count(), 5)  # 5 weeks of lessons




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
        group = Group.objects.create(
            tutor="Test Tutor",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day="14:00:00",
            lesson_length=1,  # 1 hour lessons
            associated_product=stripe_product
        )
        
        # Create a student
        student = TutoringStudent.objects.create(
            name=uniquify("Test Student"),
            parent=parent,
            active=True
        )
        student.group.add(group)

        # Schedule lessons using management command
        call_command('set_term', '2025-10-13')

        # Generate initial invoice
        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(4)  # Wait for webhooks

        # Verify initial invoice
        invoices = stripe.Invoice.list(limit=10)
        initial_invoice_found = False
        initial_invoice_id = None
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                initial_invoice_found = True
                initial_invoice_id = invoice['id']
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                self.assertEqual(len(line_items), 1)
                self.assertEqual(line_items[0]['amount'], 5000 * 1 * 2)  # $50 * 1 hour * 2 weeks
                self.assertEqual(line_items[0]['quantity'], 2)
                break

        self.assertTrue(initial_invoice_found)
        
        # Verify LocalInvoice created via webhook
        local_invoice1 = LocalInvoice.objects.get(stripeInvoiceId=initial_invoice_id)
        self.assertIsNotNone(local_invoice1)

        # TEST 1: Change price
        new_price = stripe.Price.create(
            currency="AUD",
            unit_amount=6500,  # $65 new price
            product=product.id,
        )

        time.sleep(3)
        
        # Generate invoice after price change
        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(4)

        # Verify new price is reflected
        invoices = stripe.Invoice.list(limit=20)
        price_change_invoice_found = False
        price_change_invoice_id = None
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                if len(line_items) > 0 and line_items[0]['amount'] == 6500 * 1 * 2:
                    price_change_invoice_found = True
                    price_change_invoice_id = invoice['id']
                    self.assertEqual(line_items[0]['amount'], 6500 * 1 * 2)  # $65 * 1 hour * 2 weeks
                    self.assertEqual(line_items[0]['quantity'], 2)
                    break

        self.assertTrue(price_change_invoice_found)
        
        # Verify new LocalInvoice created
        local_invoice2 = LocalInvoice.objects.get(stripeInvoiceId=price_change_invoice_id)
        self.assertIsNotNone(local_invoice2)

        # TEST 2: Change customer details
        updated_name = uniquify("John Smith Updated")
        updated_email = uniquify("johnsmith.updated@example.com")
        
        stripe.Customer.modify(
            customer.id,
            name=updated_name,
            email=updated_email,
        )

        time.sleep(3)

        # Verify parent was updated via webhook
        parent.refresh_from_db()
        self.assertEqual(parent.name, updated_name)

        # Generate invoice after customer update
        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(4)

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

        time.sleep(4)

        # Verify correct quantity for new frequency
        invoices = stripe.Invoice.list(limit=40)
        frequency_change_invoice_found = False
        frequency_change_invoice_id = None
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                # Look for the halftermly invoice (5 weeks worth)
                if len(line_items) > 0 and line_items[0]['quantity'] == 5:  # 1 hour * 5 weeks
                    frequency_change_invoice_found = True
                    frequency_change_invoice_id = invoice['id']
                    self.assertEqual(line_items[0]['amount'], 6500 * 1 * 5)  # $65 * 1 hour * 5 weeks
                    self.assertEqual(line_items[0]['quantity'], 5)
                    break

        self.assertTrue(frequency_change_invoice_found)
        
        # Verify LocalInvoice created
        local_invoice3 = LocalInvoice.objects.get(stripeInvoiceId=frequency_change_invoice_id)
        self.assertIsNotNone(local_invoice3)

        # TEST 4: Change back to original frequency and verify it still works
        parent.payment_frequency = original_frequency
        parent.save()

        generateInvoices(frequency='fortnightly', amount_of_weeks=2)

        time.sleep(4)

        # Verify we can change back successfully
        invoices = stripe.Invoice.list(limit=50)
        back_to_original_invoice_found = False
        for invoice in invoices['data']:
            if parent.stripeId == invoice['customer']:
                line_items = stripe.InvoiceItem.list(invoice=invoice.id, limit=100).to_dict()['data']
                # Look for the fortnightly invoice (2 weeks worth)
                if len(line_items) > 0 and line_items[0]['quantity'] == 2:  # 1 hour * 2 weeks
                    back_to_original_invoice_found = True
                    self.assertEqual(line_items[0]['amount'], 6500 * 1 * 2)  # $65 * 1 hour * 2 weeks
                    self.assertEqual(line_items[0]['quantity'], 2)
                    break

        self.assertTrue(back_to_original_invoice_found)

    def test_onlyTheImmediateWeeksInvoiced(self):
        name1 = uniquify("Jenny Rosen 1")
        email1 = uniquify("jennyrosen1@example.com")
        product_name1 = uniquify("Private, In Person")

        self.assertEqual(len(Parent.objects.all()), 0)
        self.assertEqual(len(StripeProd.objects.all()), 0)

        customer1 = stripe.Customer.create(
            name = name1,
            email = email1,
        )


        time.sleep(2)

        self.assertEqual(len(Parent.objects.all()), 1)
        self.assertEqual(len(StripeProd.objects.all()), 0)

        product1 = stripe.Product.create(
            name=product_name1,
        )

        # Create students
        student1 = TutoringStudent.objects.create(
            name=uniquify("Test Student1"),
            parent=Parent.objects.get(name=name1),
            active=True
        )
        
        time.sleep(3)

        stripe.Price.create(
            currency="AUD",
            unit_amount=6000,
            product=product1.id,
        )

        time.sleep(3)

        self.assertEqual(len(Parent.objects.all()), 1)
        self.assertEqual(len(StripeProd.objects.all()), 1)

        product1 = StripeProd.objects.get(name=product_name1)

        group = Group.objects.create(
            tutor="Test Tutor",
            course=Group.CourseChoices.YEAR11_ADV,
            day_of_week=Group.Weekday.MONDAY,
            time_of_day="14:00:00",
            lesson_length=1,  # 1 hour lessons
            associated_product=product1
        )

        student1.group.add(group)

        parent1 = Parent.objects.get(name=name1)
        parent1.payment_frequency = 'fortnightly'
        parent1.save()

        year = TutoringYear.objects.create(index="25")
        term = TutoringTerm.objects.create(index="4", year=year)
        # Schedule lessons using management command
        call_command('set_term', '2025-10-13')
        self.assertEqual(TutoringWeek.objects.count(), 10)
        self.assertEqual(Attendance.objects.count(), 10)
        call_command('generate_fortnightly_invoices')

        self.assertEqual(
            Attendance.objects.filter(local_invoice__isnull=False).count(), 
            2
        )
        self.assertEqual(
            Attendance.objects.filter(local_invoice__isnull=True).count(), 
            8
        )

        attendance_week_1 = Attendance.objects.select_related(
            'lesson__tutoringWeek'
        ).filter(
            lesson__tutoringWeek__index=1
        )

        attendance_week_2 = Attendance.objects.select_related(
            'lesson__tutoringWeek'
        ).filter(
            lesson__tutoringWeek__index=2
        )

        # Combine weeks 1 and 2
        attendance_week_1_and_2 = Attendance.objects.filter(
            lesson__tutoringWeek__index__in=[1, 2]
        )

        # All week 1 & 2 attendances should be invoiced
        self.assertEqual(
            attendance_week_1_and_2.filter(local_invoice__isnull=False).count(),
            attendance_week_1_and_2.count()
        )

        # All other weeks should NOT be invoiced
        attendance_other_weeks = Attendance.objects.exclude(
            lesson__tutoringWeek__index__in=[1, 2]
        )
        self.assertEqual(
            attendance_other_weeks.filter(local_invoice__isnull=True).count(),
            attendance_other_weeks.count()
        )


        '''
        4. TODO
        handles errors gracefully
        - trying to invoice inactive products
        - trying to invoice inactive parents
        - what else
        '''

        '''
        5. TODO
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