from django.shortcuts import render_to_response
from bloghub.blog.models import BlogPost

def blog(request):
    posts = BlogPost.objects.all()
    return render_to_response('archive.html', locals())
