# coding: UTF-8
from django.contrib.auth.models import User
from django.db import models

class WechatUser(models.Model):
    user = models.CharField(max_length=150)

class Product(models.Model):
    # BUY = '0'
    # SELL = '1'
    # DEAL = '2'
    # STATUS_CHOICES = (
    #     (BUY, 'buy'),
    #     (SELL, 'sell'),
    #     (DEAL, 'deal'),
    # )
    name = models.CharField(max_length=150)
    desc = models.TextField()
    price = models.IntegerField()
    timestamp = models.DateTimeField()
    user = models.ForeignKey(WechatUser)
    status = models.CharField(max_length=1)
    # status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=SELL)

class Photo(models.Model):
    product = models.ForeignKey(Product)
    picurl = models.URLField()
    mediaid = models.CharField(max_length=150)

class Location(models.Model):
    product = models.ForeignKey(Product)
    x = models.FloatField()
    y = models.FloatField()
    label = models.CharField(max_length=150)
