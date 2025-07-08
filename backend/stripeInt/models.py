from django.db import models

class StripeProd(models.Model):
  stripeId=models.CharField(max_length=20, blank=False, null=False, unique=True)
  defaultPriceId=models.CharField(max_length=20, blank=False, null=True)
  name=models.CharField(max_length=100, blank=False, null=False)
  is_active=models.BooleanField(default=True)

  def __str__(self):
    return self.name