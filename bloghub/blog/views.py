from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.template import RequestContext
from blog.forms import *
from blog.models import *
from django.contrib.auth.decorators import login_required
import pdb

pdb.set_trace()
##def blog(request):
##    posts = BlogPost.objects.all()
##    return render_to_response('archive.html', locals())
def main_page(request):
    return render_to_response('main_page.html', RequestContext(request))

def user_page(request, username):
    user = get_object_or_404(User, username=username)
    blogposts = user.blogpost_set.order_by('-id')
    if request.user.is_authenticated():
        is_friend = Friendship.objects.filter(
            from_friend=request.user,
            to_friend=user)
    else:
        is_friend = False
    variables = RequestContext(request, {
        'username':username,
        'blogposts':blogposts,
        'show_tags': True,
        'show_body': True,
        'is_friend': is_friend,
        })
    return render_to_response('user_page.html', variables)

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
            blogpost = BlogPost.objects.create(
                user=request.user)
            blogpost.body = form.cleaned_data['body']
            blogpost.title = form.cleaned_data['title']
 #           if not created:
#                blogpost.tag_set.clear()
            tag_names = form.cleaned_data['tags'].split()
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

def tag_page(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    blogposts = tag.blogposts.order_by('-id')
    variables = RequestContext(request, {
        'blogposts':blogposts,
        'tag_name':tag_name,
        'show_tags':True,
        'show_user':True,
        'show_body':True,
        })
    return render_to_response('tag_page.html', variables)

def tag_cloud_page(request):
    MAX_WEIGHT = 5
    tags = Tag.objects.order_by('name')
    # calculate tag, min and max counts.
    min_count = max_count = tags[0].blogposts.count()
    for tag in tags:
        tag.count = tag.blogposts.count()
        if tag.count < min_count:
            min_count = tag.count
        if max_count < tag.count:
            max_count = tag.count
    #calculate count range. Avoid dividing by zero.
    range = float(max_count - min_count)
    if range == 0.0:
        range = 1.0
    #calculate tag weights.
    for tag in tags:
        tag.weight = int(
            MAX_WEIGHT * (tag.count - min_count) / range
            )
    variables = RequestContext(request, {
        'tags': tags,
        })
    return render_to_response('tag_cloud_page.html', variables)

def search_page(request):
    form = SearchForm()
    blogposts = []
    show_results = False
    if 'query' in request.GET:
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query':query})
            blogposts = BlogPost.objects.filter(
                #contain operator, i stands for case-insensitive
                title__icontains=query)[:10]
    variables = RequestContext(request, {
        'form':form,
        'blogposts':blogposts,
        'show_results':show_results,
        'show_tags':True,
        'show_user':True,
        'show_body':True,
        })
    if request.GET.has_key('ajax'):
        return render_to_response('bookmark_list.html', variables)
    else:
        return render_to_response('search.html', variables)
       
def friends_page(request, username):
    user = get_object_or_404(User, username=username)
    friends = [friendship.to_friend for friendship in user.friend_set.all()]
    friend_blogposts = BlogPost.objects.filter(
        user__in=friends).order_by('-id')
    variables = RequestContext(request, {
        'username': username,
        'friends': friends,
        'blogposts': friend_blogposts[:10],
        'show_tags': True,
        'show_user': True,
        'show_body': True,
        })
    return render_to_response('friends_page.html', variables)
@login_required
def friend_add(request):
    if 'username' in request.GET:
        friend = get_object_or_404(
            User, username=request.GET['username'])
        friendship = Friendship(
            from_friend=request.user,
            to_friend=friend)
        friendship.save()
        return HttpResponseRedirect(
            '/friends/%s/' % request.user.username)
    else:
        raise Http404