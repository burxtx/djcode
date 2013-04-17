# coding: UTF-8
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

class Followingship(models.Model):
	following = models.ForeignKey(
		User, related_name='following_set'
		)
	followers = models.ForeignKey(
		User, related_name='followers_set')
	def __unicode__(self):
		return u'%s, %s' % (self.following.username,
			self.followers.username)
	class Meta:
		unique_together = (('followers', 'following'), )
