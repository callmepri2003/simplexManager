from django.db import models

class Group(models.Model):
  lesson_length = models.IntegerField(default=1)

class Lesson(models.Model):
  group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons')

class Attendance(models.Model):
  lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
  invoiced = models.BooleanField(default=False)

class Parent(models.Model):
  name = models.CharField(max_length=100)
  stripeId = models.CharField(max_length=100)
  is_active = models.BooleanField(default=True)

class Student(models.Model):
  group = models.ManyToManyField(Group, related_name='students')
  parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
