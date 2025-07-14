from abc import ABC, abstractmethod
from django.db import models
from django.dispatch import receiver
from stripeInt.models import StripeProd
from django.db.models.signals import post_save


class Group(models.Model):
  lesson_length = models.IntegerField(default=1)
  associated_product = models.ForeignKey(StripeProd, on_delete=models.CASCADE, related_name="subscribed_groups", null=True)

class Lesson(models.Model):
  group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons')

class Attendance(models.Model):
  lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
  invoiced = models.BooleanField(default=False)

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

class Student(models.Model):
  group = models.ManyToManyField(Group, related_name='students')
  parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')