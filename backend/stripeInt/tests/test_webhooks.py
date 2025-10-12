from datetime import datetime, timezone
from unittest.mock import patch
from django.test import Client, TestCase
import stripe

from tutoring.models import LocalInvoice, Parent

from stripeInt.models import StripeProd

class WebHooksTest(TestCase):
  def setUp(self):
    self.client = Client()
    self.url = "/stripe/webhooks/" 

  @patch("stripe.Webhook.construct_event")
  def testProductCreated_HappyPath(self, mock_construct_event):
    randomId = "prod_d73hg92hg82hgg0"
    mock_construct_event.return_value = {
      'type': 'product.created',
      'data': {
        'object' : {
          'id': randomId,
          'default_price': 'price_8qwbf',
          'name': 'testProduct1'
        }
      }
    }

    res = self.client.post(
      self.url,
      data=b"{}",  # Doesn't matter – it's ignored due to mocking
      content_type="application/json",
      HTTP_STRIPE_SIGNATURE="fake_signature"
    )

    product = StripeProd.objects.get(stripeId=randomId)
    self.assertIsNotNone(product)
    self.assertTrue(product.name, "testProduct1")
  
  @patch("stripe.Webhook.construct_event")
  def testProductCreated_SignatureFailed(self, mock_construct_event):
    randomId = "prod_d73hg92hg82hgg0"
    mock_construct_event.return_value = {
      'type': 'product.created',
      'data': {
        'object' : {
          'id': randomId,
          'default_price': 'price_8qwbf',
          'name': 'testProduct1'
        }
      }
    }

    mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Signature could not be verified", "Header")

    res = self.client.post(
      self.url,
      data=b"{}",  # Doesn't matter – it's ignored due to mocking
      content_type="application/json",
      HTTP_STRIPE_SIGNATURE="fake_signature"
    )
    with self.assertRaises(StripeProd.DoesNotExist):
      product = StripeProd.objects.get(stripeId=randomId)
    
  @patch("stripe.Webhook.construct_event")
  def testProductUpdated_HappyPath(self, mock_construct_event):
    randomId = "prod_d73hg92hg82hgg0"
    originalProduct = StripeProd(stripeId=randomId, name="testProduct")
    originalProduct.save()
    mock_construct_event.return_value = {
      'type': 'product.updated',
      'data': {
        'object' : {
          'id': randomId,
          'default_price': 'price_8qwbf',
          'name': 'testProductWithaChangedName'
        }
      }
    }

    res = self.client.post(
      self.url,
      data=b"{}",  # Doesn't matter – it's ignored due to mocking
      content_type="application/json",
      HTTP_STRIPE_SIGNATURE="fake_signature"
    )

    product = StripeProd.objects.get(stripeId=randomId)
    self.assertEqual(product.name, "testProductWithaChangedName")

  @patch("stripe.Webhook.construct_event")
  def testProductDeleted_HappyPath(self, mock_construct_event):
    randomId = "prod_d73hg92hg82hgg0"
    originalProduct = StripeProd(stripeId=randomId, name="testProduct")
    originalProduct.save()

    self.assertTrue(originalProduct.is_active)

    mock_construct_event.return_value = {
      'type': 'product.deleted',
      'data': {
        'object' : {
          'id': randomId,
          'default_price': 'price_8qwbf',
          'name': 'testProduct'
        }
      }
    }

    res = self.client.post(
      self.url,
      data=b"{}",  # Doesn't matter – it's ignored due to mocking
      content_type="application/json",
      HTTP_STRIPE_SIGNATURE="fake_signature"
    )

    product = StripeProd.objects.get(stripeId=randomId)
    self.assertFalse(product.is_active)
  
  @patch("stripe.Webhook.construct_event")
  def testCustomerCreated_HappyPath(self, mock_construct_event):
    randomId = "cus_SdmWpjsahaAHih"
    mock_construct_event.return_value = {
      'type': 'customer.created',
      'data': {
        'object' : {
          'id': randomId,
          'default_price': 'price_8qwbf',
          'name': 'testCustomer1'
        }
      }
    }

    res = self.client.post(
      self.url,
      data=b"{}",
      content_type="application/json",
      HTTP_STRIPE_SIGNATURE="fake_signature"
    )

    parent = Parent.objects.get(stripeId=randomId)
    self.assertIsNotNone(parent)
    self.assertTrue(parent.name, "testCustomer1")

  
  @patch("stripe.Webhook.construct_event")
  def testCustomerUpdated_HappyPath(self, mock_construct_event):
    randomId = "cus_d73hg92hg82hgg0"
    originalParent = Parent(stripeId=randomId, name="testCustomer")
    originalParent.save()
    mock_construct_event.return_value = {
      'type': 'customer.updated',
      'data': {
        'object' : {
          'id': randomId,
          'default_price': 'price_8qwbf',
          'name': 'testCustomerWithaChangedName'
        }
      }
    }

    res = self.client.post(
      self.url,
      data=b"{}",  # Doesn't matter – it's ignored due to mocking
      content_type="application/json",
      HTTP_STRIPE_SIGNATURE="fake_signature"
    )

    parent = Parent.objects.get(stripeId=randomId)
    self.assertEqual(parent.name, "testCustomerWithaChangedName")

  @patch("stripe.Webhook.construct_event")
  def testCustomerDeleted_HappyPath(self, mock_construct_event):
    randomId = "cus_d73hg92hg82hgg0"
    originalParent = Parent(stripeId=randomId, name="testCustomer")
    originalParent.save()
    self.assertTrue(originalParent.is_active)
    mock_construct_event.return_value = {
      'type': 'customer.deleted',
      'data': {
        'object' : {
          'id': randomId,
          'default_price': 'price_8qwbf',
          'name': 'testCustomer'
        }
      }
    }

    res = self.client.post(
      self.url,
      data=b"{}",  # Doesn't matter – it's ignored due to mocking
      content_type="application/json",
      HTTP_STRIPE_SIGNATURE="fake_signature"
    )

    parent = Parent.objects.get(stripeId=randomId)
    self.assertFalse(parent.is_active)

  @patch("stripe.Webhook.construct_event")
  def testInvoiceCreated_HappyPath(self, mock_construct_event):
      randomId = "in_1234567890"
      mock_construct_event.return_value = {
          'type': 'invoice.created',
          'data': {
              'object': {
                  'id': randomId,
                  'status': 'open',
                  'amount_due': 5000,
                  'amount_paid': 0,
                  'currency': 'usd',
                  'created': 1609459200,  # 2021-01-01 00:00:00 UTC
                  'status_transitions': {
                      'paid_at': None
                  },
                  'customer': 'cus_test123'
              }
          }
      }

      res = self.client.post(
          self.url,
          data=b"{}",
          content_type="application/json",
          HTTP_STRIPE_SIGNATURE="fake_signature"
      )

      invoice = LocalInvoice.objects.get(stripeInvoiceId=randomId)
      self.assertIsNotNone(invoice)
      self.assertEqual(invoice.status, 'open')
      self.assertEqual(invoice.amount_due, 5000)
      self.assertEqual(invoice.amount_paid, 0)
      self.assertEqual(invoice.currency, 'usd')
      self.assertEqual(invoice.customer_stripe_id, 'cus_test123')
      self.assertIsNone(invoice.status_transitions_paid_at)

  @patch("stripe.Webhook.construct_event")
  def testInvoiceCreated_SignatureFailed(self, mock_construct_event):
      randomId = "in_1234567890"
      mock_construct_event.side_effect = stripe.error.SignatureVerificationError(
          "Signature could not be verified", 
          "Header"
      )

      res = self.client.post(
          self.url,
          data=b"{}",
          content_type="application/json",
          HTTP_STRIPE_SIGNATURE="fake_signature"
      )

      with self.assertRaises(LocalInvoice.DoesNotExist):
          LocalInvoice.objects.get(stripeInvoiceId=randomId)

  @patch("stripe.Webhook.construct_event")
  def testInvoiceUpdated_HappyPath(self, mock_construct_event):
      randomId = "in_1234567890"
      
      # Create original invoice
      original_invoice = LocalInvoice.objects.create(
          stripeInvoiceId=randomId,
          status='open',
          amount_due=5000,
          amount_paid=0,
          currency='usd',
          created=datetime(2021, 1, 1, tzinfo=timezone.utc),
          customer_stripe_id='cus_test123'
      )

      mock_construct_event.return_value = {
          'type': 'invoice.updated',
          'data': {
              'object': {
                  'id': randomId,
                  'status': 'open',
                  'amount_due': 7500,  # Updated amount
                  'amount_paid': 0,
                  'currency': 'usd',
                  'created': 1609459200,
                  'status_transitions': {
                      'paid_at': None
                  },
                  'customer': 'cus_test123'
              }
          }
      }

      res = self.client.post(
          self.url,
          data=b"{}",
          content_type="application/json",
          HTTP_STRIPE_SIGNATURE="fake_signature"
      )

      invoice = LocalInvoice.objects.get(stripeInvoiceId=randomId)
      self.assertEqual(invoice.amount_due, 7500)

  @patch("stripe.Webhook.construct_event")
  def testInvoicePaid_HappyPath(self, mock_construct_event):
      randomId = "in_1234567890"
      paid_timestamp = 1609545600  # 2021-01-02 00:00:00 UTC
      
      # Create original unpaid invoice
      original_invoice = LocalInvoice.objects.create(
          stripeInvoiceId=randomId,
          status='open',
          amount_due=5000,
          amount_paid=0,
          currency='usd',
          created=datetime(2021, 1, 1, tzinfo=timezone.utc),
          customer_stripe_id='cus_test123'
      )

      mock_construct_event.return_value = {
          'type': 'invoice.paid',
          'data': {
              'object': {
                  'id': randomId,
                  'status': 'paid',
                  'amount_due': 5000,
                  'amount_paid': 5000,
                  'currency': 'usd',
                  'created': 1609459200,
                  'status_transitions': {
                      'paid_at': paid_timestamp
                  },
                  'customer': 'cus_test123'
              }
          }
      }

      res = self.client.post(
          self.url,
          data=b"{}",
          content_type="application/json",
          HTTP_STRIPE_SIGNATURE="fake_signature"
      )

      invoice = LocalInvoice.objects.get(stripeInvoiceId=randomId)
      self.assertEqual(invoice.status, 'paid')
      self.assertEqual(invoice.amount_paid, 5000)
      self.assertIsNotNone(invoice.status_transitions_paid_at)
      self.assertEqual(
          invoice.status_transitions_paid_at,
          datetime.fromtimestamp(paid_timestamp, tz=timezone.utc)
      )

  @patch("stripe.Webhook.construct_event")
  def testInvoicePaymentSucceeded_HappyPath(self, mock_construct_event):
      randomId = "in_1234567890"
      paid_timestamp = 1609545600
      
      # Create original unpaid invoice
      original_invoice = LocalInvoice.objects.create(
          stripeInvoiceId=randomId,
          status='open',
          amount_due=5000,
          amount_paid=0,
          currency='usd',
          created=datetime(2021, 1, 1, tzinfo=timezone.utc),
          customer_stripe_id='cus_test123'
      )

      mock_construct_event.return_value = {
          'type': 'invoice.payment_succeeded',
          'data': {
              'object': {
                  'id': randomId,
                  'status': 'paid',
                  'amount_due': 5000,
                  'amount_paid': 5000,
                  'currency': 'usd',
                  'created': 1609459200,
                  'status_transitions': {
                      'paid_at': paid_timestamp
                  },
                  'customer': 'cus_test123'
              }
          }
      }

      res = self.client.post(
          self.url,
          data=b"{}",
          content_type="application/json",
          HTTP_STRIPE_SIGNATURE="fake_signature"
      )

      invoice = LocalInvoice.objects.get(stripeInvoiceId=randomId)
      self.assertEqual(invoice.status, 'paid')
      self.assertEqual(invoice.amount_paid, 5000)

  @patch("stripe.Webhook.construct_event")
  def testInvoiceVoided_HappyPath(self, mock_construct_event):
      randomId = "in_1234567890"
      
      # Create original invoice
      original_invoice = LocalInvoice.objects.create(
          stripeInvoiceId=randomId,
          status='open',
          amount_due=5000,
          amount_paid=0,
          currency='usd',
          created=datetime(2021, 1, 1, tzinfo=timezone.utc),
          customer_stripe_id='cus_test123'
      )

      mock_construct_event.return_value = {
          'type': 'invoice.voided',
          'data': {
              'object': {
                  'id': randomId,
                  'status': 'void',
                  'amount_due': 5000,
                  'amount_paid': 0,
                  'currency': 'usd',
                  'created': 1609459200,
                  'status_transitions': {
                      'paid_at': None
                  },
                  'customer': 'cus_test123'
              }
          }
      }

      res = self.client.post(
          self.url,
          data=b"{}",
          content_type="application/json",
          HTTP_STRIPE_SIGNATURE="fake_signature"
      )

      invoice = LocalInvoice.objects.get(stripeInvoiceId=randomId)
      self.assertEqual(invoice.status, 'void')

  @patch("stripe.Webhook.construct_event")
  def testInvoiceDeleted_HappyPath(self, mock_construct_event):
      randomId = "in_1234567890"
      
      # Create original invoice
      original_invoice = LocalInvoice.objects.create(
          stripeInvoiceId=randomId,
          status='draft',
          amount_due=5000,
          amount_paid=0,
          currency='usd',
          created=datetime(2021, 1, 1, tzinfo=timezone.utc),
          customer_stripe_id='cus_test123'
      )

      mock_construct_event.return_value = {
          'type': 'invoice.deleted',
          'data': {
              'object': {
                  'id': randomId,
                  'status': 'draft',
                  'amount_due': 5000,
                  'amount_paid': 0,
                  'currency': 'usd',
                  'created': 1609459200,
                  'status_transitions': {
                      'paid_at': None
                  },
                  'customer': 'cus_test123'
              }
          }
      }

      res = self.client.post(
          self.url,
          data=b"{}",
          content_type="application/json",
          HTTP_STRIPE_SIGNATURE="fake_signature"
      )

      with self.assertRaises(LocalInvoice.DoesNotExist):
          LocalInvoice.objects.get(stripeInvoiceId=randomId)

  @patch("stripe.Webhook.construct_event")
  def testInvoiceUpdated_CreateIfNotExists(self, mock_construct_event):
      """Test that updating a non-existent invoice creates it"""
      randomId = "in_9999999999"

      mock_construct_event.return_value = {
          'type': 'invoice.updated',
          'data': {
              'object': {
                  'id': randomId,
                  'status': 'open',
                  'amount_due': 3000,
                  'amount_paid': 0,
                  'currency': 'usd',
                  'created': 1609459200,
                  'status_transitions': {
                      'paid_at': None
                  },
                  'customer': 'cus_test456'
              }
          }
      }

      res = self.client.post(
          self.url,
          data=b"{}",
          content_type="application/json",
          HTTP_STRIPE_SIGNATURE="fake_signature"
      )

      # Should create the invoice even though it didn't exist
      invoice = LocalInvoice.objects.get(stripeInvoiceId=randomId)
      self.assertIsNotNone(invoice)
      self.assertEqual(invoice.amount_due, 3000)
