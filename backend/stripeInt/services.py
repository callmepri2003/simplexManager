from tutoring.models import Parent, LocalInvoice, Attendance, Lesson
import stripe
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta, timezone
from django.db.models import Q
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

def generateInvoices(*, frequency, amount_of_weeks):
    logger.info(f"Starting {frequency} invoice generation")
    
    # Set up Stripe API key
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe.api_key:
        logger.error("Stripe API key not found in environment variables")
        return
    
    logger.debug("Stripe API key loaded successfully")
    
    # Calculate billing period
    period_start = datetime.now(timezone.utc)
    period_end = period_start + timedelta(weeks=amount_of_weeks)
    
    logger.info(f"Billing period: {period_start.date()} to {period_end.date()}")
    
    # Get all parents with matching payment frequency
    parents = Parent.objects.filter(payment_frequency=frequency, is_active=True)
    logger.info(f"Found {parents.count()} active parents with {frequency} payment frequency")
    
    # Process each parent
    for parent in parents:
        logger.debug(f"Processing parent: {parent.name} (ID: {parent.id})")
        
        # Get all children for this parent
        children = parent.children.filter(active=True)
        
        if not children.exists():
            logger.warning(f"Parent {parent.name} has no active children, skipping")
            continue
        
        # Collect all attendances for all children in this billing period
        all_attendances = []
        
        for child in children:
            logger.debug(f"Processing child: {child.name} (ID: {child.id})")
            
            # Get attendances for this child in the billing period
            attendances = Attendance.objects.filter(
                tutoringStudent=child,
                lesson__date__gte=period_start,
                lesson__date__lt=period_end,
                paid=False  # Only invoice unpaid attendances
            ).select_related('lesson', 'lesson__group', 'lesson__group__associated_product')
            
            logger.debug(f"Found {attendances.count()} unpaid attendances for {child.name}")
            all_attendances.extend(attendances)
        
        # Skip if no attendances to invoice
        if not all_attendances:
            logger.warning(f"No unpaid attendances found for parent {parent.name}, skipping")
            continue
        
        try:
            # Create Stripe invoice
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
                    }
                ]
            )
            
            logger.info(f"Created Stripe invoice {invoice.id} for parent {parent.name}")
            
            # NOTE: We don't create LocalInvoice here anymore!
            # The webhook (invoice.created) will handle creating the LocalInvoice
            # We just need to wait a moment for the webhook to process
            logger.debug(f"Waiting for webhook to create LocalInvoice for Stripe invoice {invoice.id}")
            
            # Group attendances by product for invoice items
            product_quantities = {}
            attendance_list = []
            
            for attendance in all_attendances:
                attendance_list.append(attendance)
                
                # Get the product from the group
                product = attendance.lesson.group.associated_product
                
                if not product:
                    logger.warning(f"Attendance {attendance.id} has no associated product, skipping")
                    continue
                
                # Get lesson length for this group (product is priced per hour)
                lesson_length = attendance.lesson.group.lesson_length
                
                # Count quantity per product (accounting for lesson length)
                if product.id not in product_quantities:
                    product_quantities[product.id] = {
                        'product': product,
                        'quantity': 0,
                        'student_names': set()
                    }
                
                product_quantities[product.id]['quantity'] += lesson_length
                product_quantities[product.id]['student_names'].add(attendance.tutoringStudent.name)
            
            # Create invoice items in Stripe
            for product_data in product_quantities.values():
                product = product_data['product']
                quantity = product_data['quantity']
                student_names = ', '.join(sorted(product_data['student_names']))
                
                logger.debug(f"Creating invoice item for: {product.name} (quantity: {quantity})")
                
                # Retrieve price from Stripe
                price_obj = stripe.Price.retrieve(product.defaultPriceId)
                
                # Create invoice item
                stripe.InvoiceItem.create(
                    customer=parent.stripeId,
                    unit_amount_decimal=price_obj.unit_amount,
                    currency=price_obj.currency,
                    description=f"{product.name} - {student_names}",
                    quantity=quantity,
                    invoice=invoice.id
                )
            
            # Finalize the invoice (this will trigger invoice.finalized webhook)
            finalized_invoice = stripe.Invoice.finalize_invoice(invoice.id)
            
            logger.info(f"Successfully created and finalized invoice {invoice.id} for parent {parent.name} "
                       f"with {len(all_attendances)} attendances totaling ${finalized_invoice.total / 100}")
            
            # Now link attendances to the LocalInvoice
            # We need to wait for the webhook to create the LocalInvoice first
            # In production, you might want to use a retry mechanism or celery task
            # For now, we'll try to get it with a simple retry
            local_invoice = None
            for attempt in range(3):
                try:
                    local_invoice = LocalInvoice.objects.get(stripeInvoiceId=invoice.id)
                    logger.debug(f"Found LocalInvoice {local_invoice.id} for Stripe invoice {invoice.id}")
                    break
                except LocalInvoice.DoesNotExist:
                    if attempt < 2:
                        logger.debug(f"LocalInvoice not found yet (attempt {attempt + 1}/3), waiting...")
                        import time
                        time.sleep(1)  # Wait 1 second before retry
                    else:
                        logger.warning(f"LocalInvoice not found after 3 attempts for Stripe invoice {invoice.id}")
            
            # Link attendances to local invoice if found
            if local_invoice:
                for attendance in attendance_list:
                    attendance.local_invoice = local_invoice
                Attendance.objects.bulk_update(attendance_list, ['local_invoice'])
                logger.debug(f"Linked {len(attendance_list)} attendances to LocalInvoice {local_invoice.id}")
            else:
                logger.error(f"Could not link attendances - LocalInvoice not created for {invoice.id}")
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create invoice for parent {parent.name}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error creating invoice for parent {parent.name}: {str(e)}")
            continue
    
    logger.info(f"Completed {frequency} invoice generation")

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