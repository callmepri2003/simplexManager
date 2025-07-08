from tutoring.models import Parent, Basket
import stripe
import os
from dotenv import load_dotenv
import logging
load_dotenv()

logger = logging.getLogger(__name__)

def generateFortnightlyInvoices():
    logger.info("Starting fortnightly invoice generation")
    
    # Set up Stripe API key
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe.api_key:
        logger.error("Stripe API key not found in environment variables")
        return
    
    logger.debug("Stripe API key loaded successfully")
    
    # Get all parents with fortnightly payment frequency
    parents = Parent.objects.filter(payment_frequency="fortnightly")
    logger.info(f"Found {parents.count()} parents with fortnightly payment frequency")
    
    # Process each parent
    for parent in parents:
        logger.debug(f"Processing parent ID: {parent.id}")
        
        # Check if parent has a basket
        if not parent.basket:
            logger.warning(f"Parent {parent.id} has no basket, skipping")
            continue
        
        # Get all basket items for this parent
        basket_items = parent.basket.items.all()
        
        # Skip if no items in basket
        if not basket_items.exists():
            logger.warning(f"Parent {parent.id} has no items in basket, skipping")
            continue
        
        try:
            # Create invoice items first
            for item in basket_items:
                logger.debug(f"Creating invoice item for: {item.product} (quantity: {item.quantity})")
                
                # Get the price from Stripe to get the amount
                price_obj = stripe.Price.retrieve(item.product.defaultPriceId)
                
                stripe.InvoiceItem.create(
                    customer=parent.stripeId,
                    unit_amount_decimal=price_obj.unit_amount,  # Amount in cents
                    currency=price_obj.currency,
                    description=f"Product: {item.product.stripeId}",
                    quantity=item.quantity
                )
            
            # Then create the invoice (it will automatically include all pending invoice items)
            invoice = stripe.Invoice.create(
                customer=parent.stripeId,
                auto_advance=True
            )
            
            logger.info(f"Successfully created invoice {invoice.id} for parent {parent.id}")
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create invoice for parent {parent.id}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error creating invoice for parent {parent.id}: {str(e)}")
            continue
    
    logger.info("Completed fortnightly invoice generation")