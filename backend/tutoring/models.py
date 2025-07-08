from django.db import models
from stripeInt.models import StripeProd

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
  name = models.CharField(max_length=100)
  stripeId = models.CharField(max_length=100)
  basket = models.OneToOneField(Basket, on_delete=models.DO_NOTHING, null=True)
  is_active = models.BooleanField(default=True)

class Student(models.Model):
  group = models.ManyToManyField(Group, related_name='students')
  parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
