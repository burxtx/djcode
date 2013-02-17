from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

CHOICES=(
    ('1', 'Bullshit'),
    ('2', 'Just so so'),
    ('3', 'Copied'),
    ('4', 'Help me a lot'),
    ('5', 'Awesome! Recommend!'),
    )
class Rating(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField()
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	score = models.PositiveSmallIntegerField(choices=CHOICES)
	user = models.ForeignKey(User)
