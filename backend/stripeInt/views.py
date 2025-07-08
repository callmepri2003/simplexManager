from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from abc import ABC, abstractmethod
from django.views.decorators.csrf import csrf_exempt
import os
from dotenv import load_dotenv
import stripe

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
    
    webhookHandler.handle(event['data']['object'])

    return HttpResponse(status=200)

class WebhookHandler(ABC):
    @abstractmethod
    def handle(self, data):
        pass

class CreateProductHandler(WebhookHandler):
    def handle(self, data):
        print("Creating product:", data)

class UpdateProductHandler(WebhookHandler):
    def handle(self, data):
        print("Updating product:", data)

class DeleteProductHandler(WebhookHandler):
    def handle(self, data):
        print("Deleting product:", data)
