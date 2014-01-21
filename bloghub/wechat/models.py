# coding: UTF-8
# from django.contrib.auth.models import User
from django.db import models

class Product(models.Model):
    SOLD = 0
    SALE = 1
    STATUS_CHOICES = (
        (SOLD, 'sold'),
        (SALE, 'sale'),
    )
    name = models.CharField(max_length=150)
    desc = models.TextField()
    price = models.IntegerField()
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User)
    status = models.IntegerField(choices=STATUS_CHOICES, default=SALE)

class Photo(models.Model):
    product = models.ForeignKey(Product)
    picurl = models.URLField()
    mediaid = models.CharField(max_length=150)

class Location(models.Model):
    product = models.ForeignKey(Product)
    x = models.FloatField()
    y = models.FloatField()
    label = models.CharField(max_length=150)