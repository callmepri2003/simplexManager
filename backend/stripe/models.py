from django.db import models

class StripeProd(models.Model):
  stripeId=models.CharField(max_length=20, blank=False, null=False)
  name=models.CharField(max_length=100, blank=False, null=False)