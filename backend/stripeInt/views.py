from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from abc import ABC, abstractmethod
from django.views.decorators.csrf import csrf_exempt
import os
from dotenv import load_dotenv
import stripe
from tutoring.models import Parent
from .models import StripeProd
import logging
from django.db import connection

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

@csrf_exempt
def webhooks_view(request):
    connection.close()
    logger.info(f"Webhook received: {request.method}")
    
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    webhook_secret = os.getenv('WEBHOOK_SIGNING_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        logger.info(f"Webhook event type: {event['type']}")
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponseBadRequest()
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Signature verification failed: {e}")
        return HttpResponseBadRequest()

    webhookHandler = None
    if event['type'] == 'product.created':
        webhookHandler = CreateProductHandler()
    elif event['type'] == 'product.updated':
        webhookHandler = UpdateProductHandler()
    elif event['type'] == 'product.deleted':
        webhookHandler = DeleteProductHandler()
    elif event['type'] == 'customer.created':
        webhookHandler = CreateCustomerHandler()
    elif event['type'] == 'customer.updated':
        webhookHandler = UpdateCustomerHandler()
    elif event['type'] == 'customer.deleted':
        webhookHandler = DeleteCustomerHandler()
    elif event['type'] == 'price.created':
        webhookHandler = CreatePriceHandler()
    elif event['type'] == 'price.updated':
        webhookHandler = UpdatePriceHandler()
    elif event['type'] == 'price.deleted':
        webhookHandler = DeletePriceHandler()
    else:
        logger.warning(f"Unhandled webhook event type: {event['type']}")
        return HttpResponse(status=404)
    
    logger.info(f"Processing webhook with handler: {webhookHandler.__class__.__name__}")
    webhookHandler.handle(event['data']['object'])
    logger.info(f"Successfully processed webhook: {event['type']}")

    return HttpResponse(status=200)

class WebhookHandler(ABC):
    @abstractmethod
    def handle(self, data):
        pass

class CreateProductHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Creating product: {data['id']} - {data['name']}")
        new_product = StripeProd(stripeId=data['id'], defaultPriceId=data['default_price'], name=data['name'])
        new_product.save()
        logger.info(f"Product created successfully: {data['id']}")

class UpdateProductHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Updating product: {data['id']} - {data['name']}")
        product = StripeProd.objects.get(stripeId=data['id'])
        product.name = data['name']
        product.defaultPriceId = data['default_price']
        product.save()
        logger.info(f"Product updated successfully: {data['id']}")

class DeleteProductHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Deleting product: {data['id']}")
        product = StripeProd.objects.get(stripeId=data['id'])
        product.is_active = False
        product.save()
        logger.info(f"Product deleted successfully: {data['id']}")

class CreateCustomerHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Creating customer: {data['id']} - {data['name']}")
        newParent = Parent(stripeId=data['id'], name=str(data['name']))
        newParent.save()
        logger.info(f"Customer created successfully: {data['id']}")

class UpdateCustomerHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Updating customer: {data['id']} - {data['name']}")
        parent = Parent.objects.get(stripeId=data['id'])
        parent.name = data['name']
        parent.save()
        logger.info(f"Customer updated successfully: {data['id']}")

class DeleteCustomerHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Deleting customer: {data['id']}")
        parent = Parent.objects.get(stripeId=data['id'])
        parent.is_active = False
        parent.save()
        logger.info(f"Customer deleted successfully: {data['id']}")

class CreatePriceHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Creating price: {data['id']} for product: {data['product']}")
        try:
            product = StripeProd.objects.get(stripeId=data['product'])
            product.defaultPriceId = data['id']
            product.save()
            logger.info(f"Price created and product updated successfully: {data['id']}")
        except StripeProd.DoesNotExist:
            logger.error(f"Product {data['product']} not found for price {data['id']}")
            print(f"Product {data['product']} not found for price {data['id']}")

class UpdatePriceHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Price update event received for: {data['id']} - No action taken")
        pass

class DeletePriceHandler(WebhookHandler):
    def handle(self, data):
        logger.info(f"Deleting price: {data['id']}")
        # If the deleted price was a default price, we might want to clear it
        try:
            product = StripeProd.objects.get(defaultPriceId=data['id'])
            product.defaultPriceId = None
            product.save()
            logger.info(f"Price deleted and product default price cleared: {data['id']}")
        except StripeProd.DoesNotExist:
            logger.info(f"Price {data['id']} was not a default price for any product")
            pass