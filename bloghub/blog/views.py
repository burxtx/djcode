from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.template import RequestContext
from blog.forms import *
from blog.models import *
from django.contrib.auth.decorators import login_required
import pdb
from django.utils import simplejson
from ratings.handlers import ratings, RatingHandler
from ratings.forms import StarVoteForm, SliderVoteForm
from ratings.models import Vote
from django.core.urlresolvers import reverse

ratings.register(BlogPost, form_class=StarVoteForm)
pdb.set_trace()
##def blog(request):
##    posts = BlogPost.objects.all()
##    return render_to_response('archive.html', locals())

# def main_page(request):
#     return render_to_response('main_page.html', RequestContext(request))

def user_page(request, username):
    user = get_object_or_404(User, username=username)
    # blogposts = user.blogpost_set.order_by('-id')
    blogposts = user.blogpost_set.filter(status=BlogPost.LIVE_STATUS).order_by('-id')
    if request.user.is_authenticated():
        is_following = Followingship.objects.filter(
            following=request.user,
            followers=user)
    else:
        is_following = False
    variables = RequestContext(request, {
        'username':username,
        'blogposts':blogposts,
        'show_tags': True,
        'show_body': True,
        'show_edit': username==request.user.username,
        'is_following': is_following,
        })
    return render_to_response('user_page.html', variables)

def draft_page(request, username):
    user = get_object_or_404(User, username=username)
    # drafts = user.blogpost_set.order_by('-id')
    if request.user == user:
        drafts = user.blogpost_set.filter(status=BlogPost.DRAFT_STATUS).order_by('-id')
    else:
        raise Http403
    variables = RequestContext(request, {
        'username':username,
        'drafts':drafts,
        'show_tags': True,
        'show_body': True,
        'show_edit': username==request.user.username,
        })
    return render_to_response('draft_page.html', variables)

def blogpost_detail_page(request, blogpost_id):
    if request.method == 'GET':
        blogpost = get_object_or_404(BlogPost, pk=blogpost_id)
        if blogpost:
            # cannot use _set query, because user and blogpost is not manytomany relationship
            # username = blogpost.user_set.all().values("username")[0]["username"]
            username = blogpost.user.username
        variables = RequestContext(request,{
            'blogpost': blogpost,
            'show_tags': True,
            'show_body': True,
            'show_edit': username==request.user.username,
            })
        return render_to_response('blogpost_detail.html', variables)
    elif request.method == 'POST':
        if blogpost_id:
            blogpost, created = BlogPost.objects.get_or_create(user=request.user, pk=blogpost_id)
        blogpost.title = request.POST['title']
        blogpost.body = request.POST['body']
        tag_names = request.POST.getlist('tags[]')
        blogpost.status = BlogPost.LIVE_STATUS
        for tag_name in tag_names:
            tag, dummy = Tag.objects.get_or_create(name=tag_name)
            blogpost.tag_set.add(tag)
        blogpost.save()
        # return HttpResponseRedirect('/user/%s/' % request.user.username)
        # return HttpResponseRedirect(reverse('blogpost_detail_page', args=[blogpost_id]))
        return HttpResponseRedirect('/blogpost/%s/' % blogpost_id)

def draft_detail_page(request, blogpost_id):
    draft = get_object_or_404(BlogPost, pk=blogpost_id, status=BlogPost.DRAFT_STATUS)
    if request.user.id == draft.user_id:
        if request.method == 'GET':
            variables = RequestContext(request,{
                'draft': draft,
                'show_body': True,
                'show_tags': True,
                })
            return render_to_response('draft_detail.html', variables)
    else:
        raise Http403

def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

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

def _blogpost_save(request, form, status, id=None):
    blogpost, created = BlogPost.objects.get_or_create(user=request.user, pk=id)
    # else:
    #     blogpost = BlogPost.objects.create(user=request.user)
    blogpost.body = form.cleaned_data['body']
    blogpost.title = form.cleaned_data['title']
    if not created:
        blogpost.tag_set.clear()
    tag_names = form.cleaned_data['tags'].split(',')
    blogpost.status = status
    for tag_name in tag_names:
        tag, dummy = Tag.objects.get_or_create(name=tag_name)
        blogpost.tag_set.add(tag)
    blogpost.save()
    return blogpost
# title = request.POST['title']
#         body = request.POST['title']
#         tags = request.POST['hidden-tags']
@login_required
def blogpost_save_page(request, id=None):
    if request.method == 'POST':
        tmp_req = request.POST.copy()
        tmp_req['tags'] = request.POST['hidden-tags']
        form = BlogPostSaveForm(tmp_req)
        if "submit_live" in request.POST:
            if form.is_valid():
                blogpost = _blogpost_save(request, form, BlogPost.LIVE_STATUS, id)
                return HttpResponseRedirect(
                    # reverse('user_page', args=[request.user.username])
                    '/user/%s/' % request.user.username
                    # '/blogpost/%s/' % id
                )
        # handle draft
        if "submit_draft" in request.POST:
            if form.is_valid():
                blogpost = _blogpost_save(request, form, BlogPost.DRAFT_STATUS, id)
                return HttpResponseRedirect(
                    # reverse('draft_page', args=[request.user.username])
                    '/user/%s/draft/' % request.user.username
                    # '/blogpost/%s/' % id
                )
    elif request.method == 'GET' and id:
        try:
            blogpost = BlogPost.objects.get(
                pk=id,
                user=request.user
                )
            body = blogpost.body
            title = blogpost.title
            tags = ' '.join(
                tag.name for tag in blogpost.tag_set.all()
                )
        except BlogPost.DoesNotExist:
            # restrict user to edit their own blogpost, 
            # so if others trying to access others' blog, force redirect to their own page.
            # return HttpResponseRedirect(reverse('user_page', args=[request.user.username]))
            return HttpResponseRedirect('/user/%s/' % request.user.username)
        form = BlogPostSaveForm({
            'body': body,
            'title': title,
            'tags': tags
            })
    else:
        form = BlogPostSaveForm()
    variables = RequestContext(request, {
        'user': request.user,
        'form':form
        })
    return render_to_response('blogpost_save.html', variables)

@login_required
def blogpost_delete(request, id=None):
    username = request.user.username
    blogpost = get_object_or_404(BlogPost, pk=id)
    blogpost.delete()
    results={'success': True}
    json = simplejson.dumps(results)
    # return HttpResponse()
    # return HttpResponse(json, mimetype='application/json')
    if request.is_ajax():
        return HttpResponse(json, mimetype='application/json')
    else:
        return HttpResponseRedirect('/user/%s/' % username)
    # return HttpResponseRedirect(reverse('user_page', args=(username,)))
    # return HttpResponseRedirect('/user/%s/' % username)

def tag_page(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    blogposts = tag.blogposts.filter(status=BlogPost.LIVE_STATUS).order_by('-id')
    variables = RequestContext(request, {
        'blogposts':blogposts,
        'tag_name':tag_name,
        'show_tags':True,
        'show_user':True,
        'show_body':True,
        })
    return render_to_response('tag_page.html', variables)

# def tag_cloud_page(request):
@login_required
def main_page(request):
    import recommendations as rec
    # recommended posts
    # get user data
    user = request.user
    handler = ratings.get_handler(BlogPost)
    # others = User.objects.filter().exclude(username=user)
    # for test all users
    users = User.objects.all()
    critics = {}
    for other in users:
        scores = {}
        for vote in ratings.get_votes_by(other):
            scores[vote.content_object.title] = vote.score
            # print "%s -> %s" % (vote.content_object.title, vote.score)
        if scores != {}:
            critics[other] = scores
    print rec.getRecommendations(critics, user)
        
    # latest avtivities from following people
    following_people = [followingship.followers for followingship in user.following_set.all()]
    following_people_blogposts = BlogPost.objects.filter(
        user__in=following_people,
        status=BlogPost.LIVE_STATUS,
        ).order_by('-id')


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
        # 'username': user,
        'following_people': following_people,
        'blogposts': following_people_blogposts,
        'show_tags': True,
        'show_user': True,
        'show_body': True,
        'tags': tags,
        })
    # return render_to_response('tag_cloud_page.html', variables)
    return render_to_response('main_page.html', variables)

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
                status=BlogPost.LIVE_STATUS,
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
        return render_to_response('blogpost_list.html', variables)
    else:
        return render_to_response('search.html', variables)
       
def friends_page(request, username):
    user = get_object_or_404(User, username=username)
    following_people = [followingship.followers for followingship in user.following_set.all()]
    following_people_blogposts = BlogPost.objects.filter(
        user__in=following_people,
        status=BlogPost.LIVE_STATUS,
        ).order_by('-id')
    variables = RequestContext(request, {
        'username': username,
        'following_people': following_people,
        'blogposts': following_people_blogposts[:10],
        'show_tags': True,
        'show_user': True,
        'show_body': True,
        })
    return render_to_response('friends_page.html', variables)

@login_required
def friend_add(request):
    # if 'username' in request.GET:
    #     friend = get_object_or_404(
    #         User, username=request.GET['username'])
    #     followingship, is_following = Followingship.objects.get_or_create(
    #         following=request.user,
    #         followers=friend)
    #     return HttpResponseRedirect(
    #         '/following/%s/' % request.user.username)
    # else:
    #     raise Http404

    if 'username' in request.GET:
        friend = get_object_or_404(User, username=request.GET['username'])
        followingship, is_following = Followingship.objects.get_or_create(
            following=request.user,
            followers=friend)
        results={'success': True}
        json = simplejson.dumps(results)
        # return HttpResponse()
        return HttpResponse(json, mimetype='application/json')
    else:
        raise Http404

@login_required
def friend_remove(request):
    if 'username' in request.GET:
        friend = get_object_or_404(User, username=request.GET['username'])
        followingship = Followingship.objects.filter(
            following=request.user, 
            followers=friend).delete()
        results={'success': True}
        json = simplejson.dumps(results)
        # return HttpResponse()
        return HttpResponse(json, mimetype='application/json')
    else:
        raise Http404

def ajax_tag_autocomplete(request):
    if 'q' in request.GET:
        tags = Tag.objects.filter(name__isstartswith=request.GET['q'])[:10]
        return HttpResponse(u'\n'.join(tag.name for tag in tags))
    return HttpResponse()