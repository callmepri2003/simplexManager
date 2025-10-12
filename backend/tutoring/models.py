from abc import ABC, abstractmethod
from decimal import Decimal
import os
from django.db import models
from django.dispatch import receiver
from stripeInt.models import StripeProd
from django.db.models.signals import post_save
import base64

class LocalInvoice(models.Model):
    """
    Local copy of essential Stripe invoice data for revenue calculations.
    Synced via webhooks. Use get_stripe_invoice() for full invoice data.
    """
    stripeInvoiceId = models.CharField(max_length=255, unique=True, db_index=True)
    
    # Essential fields for revenue calculations
    status = models.CharField(max_length=50)  # paid, open, void, uncollectible, etc.
    amount_due = models.IntegerField()  # in cents
    amount_paid = models.IntegerField(default=0)  # in cents
    currency = models.CharField(max_length=3, default='usd')
    
    # Timestamps for revenue reporting
    created = models.DateTimeField()  # When invoice was created in Stripe
    status_transitions_paid_at = models.DateTimeField(null=True, blank=True)  # When it was paid
    
    # Metadata
    customer_stripe_id = models.CharField(max_length=255, null=True, blank=True)
    last_synced = models.DateTimeField(auto_now=True)
    
    def get_stripe_invoice(self):
        """Fetch the full invoice data from Stripe when needed"""
        import stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        return stripe.Invoice.retrieve(self.stripeInvoiceId)
    
    def is_paid(self):
        """Check if invoice is paid using local data"""
        return self.status == 'paid'
    
    def get_amount_in_dollars(self):
        """Convert cents to dollars"""
        return self.amount_paid / 100
    
    def __str__(self):
        return f"Invoice {self.stripeInvoiceId} - {self.status} - ${self.get_amount_in_dollars()}"
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'status_transitions_paid_at']),  # For revenue queries
            models.Index(fields=['created']),
        ]

class Group(models.Model):
    class CourseChoices(models.TextChoices):
        JUNIOR_MATHS = "Junior Maths", "Junior Maths"
        YEAR11_ADV = "11 Advanced", "11 Advanced"
        YEAR11_EXT1 = "11 Ext 1", "11 Ext 1"
        YEAR12_ADV = "12 Advanced", "12 Advanced"
        YEAR12_EXT1 = "12 Ext 1", "12 Ext 1"
        YEAR12_EXT2 = "12 Ext 2", "12 Ext 2"

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    lesson_length = models.IntegerField()

    associated_product = models.ForeignKey(
        StripeProd,
        on_delete=models.CASCADE,
        related_name="subscribed_groups",
        null=True
    )

    tutor = models.CharField(max_length=50)
    course = models.CharField(
        max_length=20,
        choices=CourseChoices.choices,
        null=True
    )
    day_of_week = models.IntegerField(
        choices=Weekday.choices,
        null=True
    )
    time_of_day = models.TimeField(null=True)

    # real storage
    image_base64 = models.TextField(null=True, blank=True)

    # transient upload field (not stored in DB)
    image_upload = models.FileField(upload_to="tmp/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.image_upload:
            # read and convert to base64
            self.image_base64 = base64.b64encode(self.image_upload.read()).decode("utf-8")
            # clear the temp file field so it's not persisted
            self.image_upload.delete(save=False)
            self.image_upload = None
        super().save(*args, **kwargs)

    def __str__(self):
        try:
          return f"{self.course} with {self.tutor} on {self.get_day_of_week_display()} at {self.time_of_day.strftime('%I:%M %p')}"
        except:
           return ""

class Lesson(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="lessons")
    notes = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField()

    def __str__(self):
        return f"Lesson {self.id} - {self.notes or 'No notes'}"

@receiver(post_save, sender=Lesson)
def create_lesson_attendances(sender, instance, created, **kwargs):
    """
    Creates attendance records for all students in the group when a lesson is created.
    """
    if created:
        
        students = instance.group.tutoringStudents.all()
        
        for student in students:
            Attendance.objects.create(
                lesson=instance,
                tutoringStudent=student,
                present=False,
                homework=False,
                paid=False
            )


class Resource(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    file = models.FileField(upload_to='trial1/')
    name = models.CharField(max_length=200)
    
    def save(self, *args, **kwargs):
        print(f"About to save file: {self.file.name if self.file else 'No file'}")
        result = super().save(*args, **kwargs)
        if self.file:
            print(f"File saved to: {self.file.url}")
            print(f"File storage: {type(self.file.storage)}")
        return result

class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
    tutoringStudent = models.ForeignKey("TutoringStudent", on_delete=models.DO_NOTHING, related_name='lessons_attended')
    homework = models.BooleanField(default=False)
    present = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    local_invoice = models.ForeignKey(LocalInvoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendances')

class Parent(models.Model):
    PAYMENT_FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('half-termly', 'Half-Termly'),
        ('termly', 'Termly'),
    ]

    name = models.CharField(max_length=100)
    stripeId = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        default='half-termly',
    )

    def __str__(self):
        return self.name

class TutoringStudent(models.Model):
  name = models.CharField(max_length=100)
  group = models.ManyToManyField(Group, related_name='tutoringStudents')
  parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
  active = models.BooleanField(default=False, null=False)
  start_date = models.DateField(auto_now_add=True, null=False, blank=False)
  end_date = models.DateField(null=True, blank=True)
  

  def __str__(self):
      return self.name