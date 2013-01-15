from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.forms import ModelForm, get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

from reviews.models import Review

class ReviewForm(object):
	"""docstring for ReviewForm"""
	class Meta:
		model = Review
		# fields = ('user_name', 'user_email', 'comment', 'score')
		fields = ('comment', 'score')

def ReviewForm(request):
	if request.method == "POST":
    form = ReviewForm(request.POST)
        if form.is_valid():
        	review = Review.objects.create(
        		user=request.user)
            review.score = form.cleaned_data['score']
            review.comment = form.cleaned_data['comment']
            review.save()
            return HttpResponseRedirect(
                '/blogpost/%s/' % 
            )

    else:
    	form = ReviewForm
    variables = RequestContext(request, {
        'form':form
        })
    return render_to_response('review_save.html', variables)
