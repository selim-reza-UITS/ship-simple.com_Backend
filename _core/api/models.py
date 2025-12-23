# models.py

from django.db import models

class ShippingRate(models.Model):
    origin_country = models.CharField(max_length=5, choices=[('USA', 'USA'), ('UK', 'UK')])
    min_weight = models.FloatField(default=0.0)
    max_weight = models.FloatField()
    price = models.FloatField()

    class Meta:
        ordering = ['origin_country', 'min_weight']

    def __str__(self):
        return f"{self.origin_country}: {self.min_weight}kg - {self.max_weight}kg = ${self.price}"

class Category(models.Model):
    name = models.CharField(max_length=50)
    duty_rate = models.FloatField()  # Duty rate for this category

    def __str__(self):
        return self.name

class ShippingConfig(models.Model):
    vat_rate = models.FloatField(default=0.175)  # Default 17.5%
    local_handling_fee = models.FloatField(default=25.0)  # Default handling fee
    margin_rate = models.FloatField(default=0.15)  # Default margin of 15%

    def __str__(self):
        return "Shipping Configuration"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
