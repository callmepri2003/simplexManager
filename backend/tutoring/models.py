from abc import ABC, abstractmethod
from django.db import models
from django.dispatch import receiver
from stripeInt.models import StripeProd
from django.db.models.signals import post_save
import base64


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

    lesson_length = models.IntegerField(default=1)  # In hours
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
#   present = models.BooleanField(default=False)
  paid = models.BooleanField(default=False)



class Basket(models.Model):
  None

class BasketItem(models.Model):
  basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
  product = models.ForeignKey(StripeProd, on_delete=models.CASCADE, related_name="basketItems")
  quantity = models.IntegerField()

class Parent(models.Model):
    PAYMENT_FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('fortnightly', 'Fortnightly'),
        ('half-termly', 'Half-Termly'),
        ('termly', 'Termly'),
    ]

    name = models.CharField(max_length=100)
    stripeId = models.CharField(max_length=100)
    basket = models.OneToOneField('Basket', on_delete=models.DO_NOTHING, null=True)
    is_active = models.BooleanField(default=True)
    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        default='half-termly',
    )
      

@receiver(post_save, sender=Parent)
def create_parent_basket(sender, instance, created, **kwargs):
    """
    Creates an empty basket for a parent when the parent is first created.
    """
    if created and not instance.basket:
        basket = Basket.objects.create()
        instance.basket = basket
        instance.save()

class TutoringStudent(models.Model):
  name = models.CharField(max_length=100)
  group = models.ManyToManyField(Group, related_name='tutoringStudents')
  parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')