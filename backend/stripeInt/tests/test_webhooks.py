from unittest.mock import patch
from django.test import Client, TestCase
import stripe

from tutoring.models import Parent

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
