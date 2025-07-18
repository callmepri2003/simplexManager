from tutoring.models import Parent, Basket
import stripe
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
load_dotenv()

logger = logging.getLogger(__name__)

def generateWeeklyInvoices():
    generateInvoices(frequency="weekly", amount_of_weeks=1)

def generateFortnightlyInvoices():
    generateInvoices(frequency="fortnightly", amount_of_weeks=2)

def generateHalfTermlyInvoices():
    generateInvoices(frequency="half-termly", amount_of_weeks=5)

def generateTermlyInvoices():
    generateInvoices(frequency="termly", amount_of_weeks=10)

def generateInvoices(*, frequency, amount_of_weeks ):
    logger.info(f"Starting {frequency} invoice generation")
    
    # Set up Stripe API key
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe.api_key:
        logger.error("Stripe API key not found in environment variables")
        return
    
    logger.debug("Stripe API key loaded successfully")
    
    # Get all parents with fortnightly payment frequency
    parents = Parent.objects.filter(payment_frequency=frequency)
    logger.info(f"Found {parents.count()} parents with {frequency} payment frequency")
    
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
            # Create invoice items
            # Then create the invoice (it will automatically include all pending invoice items)
            invoice = stripe.Invoice.create(
                customer=parent.stripeId,
                auto_advance=True,
                collection_method="send_invoice",
                days_until_due=amount_of_weeks * 7,
                custom_fields=[
                    {
                        "name": "Billing Period",
                        "value": calculate_billing_period(amount_of_weeks)
                    },
                    {
                        "name": "Payment Frequency",
                        "value": frequency
                    },
                    {
                        "name": "Hotel",
                        "value": "Trivago"
                    }
                ]
            )

            for item in basket_items:
                logger.debug(f"Creating invoice item for: {item.product} (quantity: {item.quantity})")

                price_obj = stripe.Price.retrieve(item.product.defaultPriceId)
                
                stripe.InvoiceItem.create(
                    customer=parent.stripeId,
                    unit_amount_decimal=price_obj.unit_amount,
                    currency=price_obj.currency,
                    description=f"Product: {item.product.stripeId}",
                    quantity=item.quantity * amount_of_weeks,
                    invoice=invoice.id
                )
            
            
            
            logger.info(f"Successfully created invoice {invoice.id} for parent {parent.id}")
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create invoice for parent {parent.id}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error creating invoice for parent {parent.id}: {str(e)}")
            continue
    
    logger.info("Completed fortnightly invoice generation")

def calculate_billing_period(amount_of_weeks):
    """
    Calculate human-readable billing period from today to today + amount_of_weeks (exclusive end date)
    
    Args:
        amount_of_weeks (int): Number of weeks for the billing period
        
    Returns:
        str: Formatted billing period (e.g., "Monday 19th July to Sunday 1st August")
    """
    start_date = datetime.now()
    end_date = start_date + timedelta(weeks=amount_of_weeks, days=-1)
    
    def get_ordinal_suffix(day):
        if 10 <= day % 100 <= 20:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    
    start_formatted = start_date.strftime(f"%A %d{get_ordinal_suffix(start_date.day)} %B")
    end_formatted = end_date.strftime(f"%A %d{get_ordinal_suffix(end_date.day)} %B")
    
    return f"{start_formatted} to {end_formatted}"