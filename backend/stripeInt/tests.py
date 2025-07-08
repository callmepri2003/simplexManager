from unittest.mock import patch
from django.test import Client, TestCase
import stripe

from .models import StripeProd

class WebHooksTest(TestCase):
  def setUp(self):
    self.client = Client()
    self.url = "/stripe/webhooks/" 

  @patch("stripe.Webhook.construct_event")
  def testProductCreated(self, mock_construct_event):
    randomId = "prod_d73hg92hg82hgg0"
    mock_construct_event.return_value = {
      'type': 'product.created',
      'data': {
        'object' : {
          'id': randomId,
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

  # @patch("stripe.Webhook.construct_event")
  # def testProductUpdated(self, mock_construct_event):
  #   randomId = "prod_d73hg92hg82hgg0"
  #   mock_construct_event.return_value = {
  #     'type': 'product.updated',
  #     'data': {
  #       'object' : {
  #         'id': randomId,
  #         'name': 'testProduct1'
  #       }
  #     }
  #   }

  #   res = self.client.post(
  #     self.url,
  #     data=b"{}",  # Doesn't matter – it's ignored due to mocking
  #     content_type="application/json",
  #     HTTP_STRIPE_SIGNATURE="fake_signature"
  #   )

  #   product = StripeProd.objects.get(stripeId=randomId)
  #   self.assertIsNotNone(product)
  #   self.assertTrue(product.name, "testProduct1")
    
