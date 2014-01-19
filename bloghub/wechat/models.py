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
    timestamp = models.DateTimeField()
    # user = models.ForeignKey(User)
    user = models.CharField(max_length=150)
    locationX = models.FloatField()
    locationY = models.FloatField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=SALE)
    def __str__(self):
        return '%s, %s' % (self.user.username, self.title)

