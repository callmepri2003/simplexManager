from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from abc import ABC, abstractmethod
from django.views.decorators.csrf import csrf_exempt
import os
from dotenv import load_dotenv
import stripe
from tutoring.models import Parent
from .models import StripeProd

load_dotenv()

@csrf_exempt
def webhooks_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    webhook_secret = os.getenv('WEBHOOK_SIGNING_SECRET')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return HttpResponseBadRequest()
    except stripe.error.SignatureVerificationError as e:
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
        return HttpResponse(status=200)
    
    webhookHandler.handle(event['data']['object'])

    return HttpResponse(status=200)

class WebhookHandler(ABC):
    @abstractmethod
    def handle(self, data):
        pass

class CreateProductHandler(WebhookHandler):
    def handle(self, data):
        print(data)
        new_product = StripeProd(stripeId=data['id'], defaultPriceId=data['default_price'], name=data['name'])
        new_product.save()

class UpdateProductHandler(WebhookHandler):
    def handle(self, data):
        product = StripeProd.objects.get(stripeId=data['id'])
        product.name = data['name']
        product.defaultPriceId = data['default_price']
        product.save()

class DeleteProductHandler(WebhookHandler):
    def handle(self, data):
        product = StripeProd.objects.get(stripeId=data['id'])
        product.is_active = False
        product.save()

class CreateCustomerHandler(WebhookHandler):
    def handle(self, data):
        newParent = Parent(stripeId=data['id'], name=str(data['name']))
        newParent.save()

class UpdateCustomerHandler(WebhookHandler):
    def handle(self, data):
        parent = Parent.objects.get(stripeId=data['id'])
        parent.name = data['name']
        parent.save()

class DeleteCustomerHandler(WebhookHandler):
    def handle(self, data):
        parent = Parent.objects.get(stripeId=data['id'])
        parent.is_active = False
        parent.save()
class CreatePriceHandler(WebhookHandler):
    def handle(self, data):
        print(data)
        try:
            product = StripeProd.objects.get(stripeId=data['product'])
            product.defaultPriceId = data['id']
            product.save()
        except StripeProd.DoesNotExist:
            print(f"Product {data['product']} not found for price {data['id']}")

class UpdatePriceHandler(WebhookHandler):
    def handle(self, data):
        pass

class DeletePriceHandler(WebhookHandler):
    def handle(self, data):
        # If the deleted price was a default price, we might want to clear it
        try:
            product = StripeProd.objects.get(defaultPriceId=data['id'])
            product.defaultPriceId = None
            product.save()
        except StripeProd.DoesNotExist:
            pass