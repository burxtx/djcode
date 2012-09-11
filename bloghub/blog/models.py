from django.contrib.auth.models import User
from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=150)
    body = models.TextField()
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User)
    
