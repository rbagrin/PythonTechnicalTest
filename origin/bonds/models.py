from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Bond(models.Model):
    isin = models.CharField(max_length=12, blank=False)
    size = models.DecimalField(max_digits=24, decimal_places=4, null=True)
    currency = models.CharField(max_length=3, blank=False)
    maturity = models.DateField()
    lei = models.CharField(max_length=20, blank=False)
    legal_name = models.CharField(max_length=255, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
