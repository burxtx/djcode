from django.db import models
from django.contrib.auth.models import User

class Review(model.Model):
	user = models.ForeignKey(User)
	user_name = models.CharField(max_length=50)
	user_email = models.EmailField()

	score = models.FloatField(choices=SCORE_RANGE, default=3.0)
	comment = model.TextField(max_length=255)
	pub_date = models.DateTimeField(auto_now_add=True)
	
	class Meta:
        ordering = ("-pub_date", )

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.score)

	@property
    def name(self):
        """Returns the stored user name.
        """
        if self.user is not None:
            return self.user.get_full_name()
        else:
            return self.user_name

    @property
    def email(self):
        """Returns the stored user email.
        """
        if self.user is not None:
            return self.user.email
        else:
            return self.user_email
