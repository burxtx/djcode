from django.contrib.auth.models import User
from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=150)
    body = models.TextField()
##    timestamp = models.DateTimeField()
    user = models.ForeignKey(User)
    def __str__(self):
        return '%s, %s' % (self.user.username, self.title)
    
class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    blogposts = models.ManyToManyField(BlogPost)
    def __str__(self):
        return self.name
