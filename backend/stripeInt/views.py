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
    
    webhookHandler.handle(event['data']['object'])

    return HttpResponse(status=200)

class WebhookHandler(ABC):
    @abstractmethod
    def handle(self, data):
        pass

class CreateProductHandler(WebhookHandler):
    def handle(self, data):
        new_product = StripeProd(stripeId=data['id'], name=data['name'])
        new_product.save()

class UpdateProductHandler(WebhookHandler):
    def handle(self, data):
        product = StripeProd.objects.get(stripeId=data['id'])
        product.name = data['name']
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