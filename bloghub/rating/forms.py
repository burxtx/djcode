import re
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django import forms

CHOICES=(
    ('1', 'Bullshit'),
    ('2', 'Just so so'),
    ('3', 'Copied'),
    ('4', 'Help me a lot'),
    ('5', 'Awesome! Recommend!'),
    )

class AddRateForm(forms.Form):
    score = forms.IntegerField(widget=forms.RadioSelect, choice=CHOICES)