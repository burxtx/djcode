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

class Friendship(models.Model):
	from_friend = models.ForeignKey(
		User, related_name='friend_set'
		)
	to_friend = models.ForeignKey(
		User, related_name='to_friend_set')
	def __unicode__(self):
		return u'%s, %s' % (self.from_friend.username,
			self.to_friend.username)
	class Meta:
		unique_together = (('to_friend', 'from_friend'), )