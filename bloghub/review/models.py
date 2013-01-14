from django.db import models
from django.contrib.auth.models import User

class Review(model.Model):
	user = models.ForeignKey(User)
	score = models.FloatField(choices=SCORE_RANGE, default=3.0)
