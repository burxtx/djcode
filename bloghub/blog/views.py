from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.template import RequestContext
from blog.forms import *
from blog.models import *
from django.contrib.auth.decorators import login_required

def blog(request):
    posts = BlogPost.objects.all()
    return render_to_response('archive.html', locals())
def main_page(request):
    return render_to_response('main_page.html', RequestContext(request))

def user_page(request, username):
    try:
        user = User.objects.get(username=username)
    except:
        raise Http404('Requested user not found')
    blogs = user.blogpost_set.all()
    return render_to_response('user_page.html', {
        'username':username,
        'bblogs':blogs,})

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                )
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
        'form':form
        })
    return render_to_response('registration/register.html', variables)

@login_required
def blogpost_save_page(request):
    if request.method == 'POST':
        form = BlogPostSaveForm(request.POST)
        if form.is_valid():
            blogpost, created = BlogPost.objects.get_or_create(
                user=request.user)
            blogpost.title = form.clean_data['title']
            if not created:
                blogpost.tag_set.clear()
            tag_names = form.clean_data['tags'].split()
            for tag_name in tag_names:
                tag, dummy = Tag.objects.get_or_create(name=tag_name)
                blogpost.tag_set.add(tag)
            blogpost.save()
            return HttpResponseRedirect(
                '/user/%s/' % request.user.username
            )
    else:
        form = BlogPostSaveForm()
    variables = RequestContext(request, {
        'form':form
        })
    return render_to_response('blogpost_save.html', variables)
            
