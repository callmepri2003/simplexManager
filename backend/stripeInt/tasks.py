import logging

logger = logging.getLogger(__name__)

def doThis():
    logger.info("Starting invoice generation...")
    # Your logic here (same as before)
    logger.info("Invoice generation completed")
    return "Invoices generated successfully"
