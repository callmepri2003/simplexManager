from tutoring.models import Parent, LocalInvoice, Attendance, Lesson, TutoringWeek, TutoringTerm
import stripe
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta, timezone
from django.db.models import Q
load_dotenv()

logger = logging.getLogger(__name__)

def generateWeeklyInvoices():
    generateInvoices(frequency="weekly", weeks_to_include=1)

def generateFortnightlyInvoices():
    generateInvoices(frequency="fortnightly", weeks_to_include=2)

def generateHalfTermlyInvoices():
    generateInvoices(frequency="half-termly", weeks_to_include=5)

def generateTermlyInvoices():
    generateInvoices(frequency="termly", weeks_to_include=10)

def get_weeks_to_invoice(weeks_to_include):
    """
    Get the TutoringWeeks to invoice based on current date.
    Returns weeks starting from the current week (or next if current is past).
    
    Args:
        weeks_to_include (int): Number of weeks to include in the invoice
        
    Returns:
        QuerySet of TutoringWeek objects
    """
    today = datetime.now().date()
    
    # Find the current week (or next upcoming week if we're between terms)
    current_week = TutoringWeek.objects.filter(
        monday_date__lte=today,
        sunday_date__gte=today
    ).first()
    
    if not current_week:
        # If no current week found, get the next upcoming week
        current_week = TutoringWeek.objects.filter(
            monday_date__gt=today
        ).order_by('monday_date').first()
        
        if not current_week:
            logger.warning("No current or upcoming tutoring weeks found")
            return TutoringWeek.objects.none()
    
    logger.info(f"Current week: {current_week} ({current_week.monday_date} to {current_week.sunday_date})")
    
    # Get the term and calculate which weeks to include
    term = current_week.term
    current_week_index = current_week.index
    
    # Calculate the range of week indices to include
    end_week_index = current_week_index + weeks_to_include - 1
    
    # Get all weeks in the range from the same term
    weeks = TutoringWeek.objects.filter(
        term=term,
        index__gte=current_week_index,
        index__lte=end_week_index
    ).order_by('index')
    
    logger.info(f"Invoicing weeks {current_week_index} to {end_week_index} in {term}")
    
    return weeks

def generateInvoices(*, frequency, weeks_to_include):
    logger.info(f"Starting {frequency} invoice generation")
    
    # Set up Stripe API key
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    if not stripe.api_key:
        logger.error("Stripe API key not found in environment variables")
        return
    
    logger.debug("Stripe API key loaded successfully")
    
    # Get the weeks to invoice
    weeks_to_invoice = get_weeks_to_invoice(weeks_to_include)
    
    if not weeks_to_invoice.exists():
        logger.warning("No weeks to invoice, exiting")
        return
    
    week_ids = list(weeks_to_invoice.values_list('id', flat=True))
    logger.info(f"Will invoice {len(week_ids)} weeks: {list(weeks_to_invoice.values_list('index', flat=True))}")
    
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
        
        # Collect all attendances for all children across the specified weeks
        all_attendances = []
        
        for child in children:
            logger.debug(f"Processing child: {child.name} (ID: {child.id})")
            
            # Get attendances for this child from lessons in the specified weeks
            attendances = Attendance.objects.filter(
                tutoringStudent=child,
                lesson__tutoringWeek__id__in=week_ids,  # Filter by the specific weeks
                paid=False,  # Only invoice unpaid attendances
                local_invoice__isnull=True  # Not already invoiced
            ).select_related('lesson', 'lesson__group', 'lesson__group__associated_product', 'lesson__tutoringWeek')
            
            logger.debug(f"Found {attendances.count()} unpaid attendances for {child.name} in weeks {list(weeks_to_invoice.values_list('index', flat=True))}")
            all_attendances.extend(attendances)
        
        
        # Skip if no attendances to invoice
        if not all_attendances:
            logger.warning(f"No unpaid attendances found for parent {parent.name} in the selected weeks, skipping")
            continue
        
        try:
            # Calculate billing period description
            first_week = weeks_to_invoice.first()
            last_week = weeks_to_invoice.last()
            billing_period = f"{first_week.term} Weeks {first_week.index}-{last_week.index}"
            if first_week.monday_date and last_week.sunday_date:
                billing_period += f" ({first_week.monday_date.strftime('%d/%m')} - {last_week.sunday_date.strftime('%d/%m/%Y')})"
            
            # Create Stripe invoice
            invoice = stripe.Invoice.create(
                customer=parent.stripeId,
                auto_advance=True,
                collection_method="send_invoice",
                days_until_due=weeks_to_include * 7,
                custom_fields=[
                    {
                        "name": "Billing Period",
                        "value": billing_period
                    },
                    {
                        "name": "Payment Frequency",
                        "value": frequency
                    }
                ]
            )
            
            logger.info(f"Created Stripe invoice {invoice.id} for parent {parent.name}")
            
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

def calculate_billing_period_from_weeks(weeks_count):
    """
    Calculate human-readable billing period for a given number of weeks.
    
    Args:
        weeks_count (int): Number of weeks for the billing period
        
    Returns:
        str: Formatted billing period (e.g., "Weeks 1-2" or "Weeks 1-5")
    """
    if weeks_count == 1:
        return "1 week"
    else:
        return f"{weeks_count} weeks"