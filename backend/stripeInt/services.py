from tutoring.models import Parent
import stripe
import os
from dotenv import load_dotenv
load_dotenv()

def generateFortnightlyInvoices():
  stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
  for parent in Parent.objects.filter(payment_frequency="fortnightly"):
    
    for item in parent.basket.basketItems:
      stripe.InvoiceItem.create(
        customer=parent.stripeId,
        price=item.product.stripeId,
        quantity=item.quantity
      )

    invoice = stripe.Invoice.create(
      customer=parent.stripeId,
      auto_advance=True
    )
