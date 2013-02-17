from ContentType.contents.models import *
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db import models
from rating.models import *
from rating.forms import *
import pdb

pdb.set_trace()
@login_required
def add_rate(request):
	if request.method == 'POST':
		data = request.POST.copy()
		ctype = data.get("content_type")
		object_pk = data.get("object_pk")
		form = AddRateForm(request.POST)
		if form.is_valid():
			score = form.cleaned_data['score']
    		content_object = ContentType.objects.get(pk=ctype.pk).get_object_for_this_type(pk=object_pk)
			rating = Rating.objects.get_or_create(content_object=content_object, score=score, rater=request.user)
			rating.save()
			return HttpResponseRedirect('.')
	else:
		form = AddRateForm()
	variables = RequestContext(request, {
        'form':form
        })
	return render_to_response('rating/rating.html', variables)
