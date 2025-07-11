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
from .services import generateFortnightlyInvoices

load_dotenv()

class ServicesTest(StaticLiveServerTestCase):
  @classmethod
  def setUpClass(cls):
      super().setUpClass()
      stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

      print(f"Live server URL: {cls.live_server_url}")
      webhook_url = f"{cls.live_server_url}/stripe/webhooks/"
      print(f"Webhook URL: {webhook_url}")
      
      # Test that the server is actually reachable
      import requests
      try:
          response = requests.get(cls.live_server_url)
          print(f"Server test: {response.status_code}")
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
                print(f"Found webhook secret: {webhook_secret}")
                os.environ['WEBHOOK_SIGNING_SECRET'] = webhook_secret
                break
        
        # Break when we see "Ready!" to avoid blocking
        if "Ready!" in line:
            break

      
      # Wait for listener to start
      print(f"Stripe listener started, forwarding to: {webhook_url}")

      
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

    generateFortnightlyInvoices()

    invoices = stripe.Invoice.list(limit=10)
    customerFound = False
    for invoice in invoices['data']:
       if(parent.stripeId == invoice['customer']):
          customerFound = True

    self.assertTrue(customerFound)
    # i want to assert that an invoice is 
    # targeted to the person above
  


  '''
  2.
  Correctly invoicing the correct quantities,
  fortnightly group
  half termly group
  half termly private
  fortnightly group
  etc
  '''


  '''
  3.
  responds gracefully to:
  - changing prices
  - changing customer details
  - changing customer payment frequencies
  '''


  '''
  4.
  handles errors gracefully
  - trying to invoice inactive products
  - trying to invoice inactive parents
  - what else
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