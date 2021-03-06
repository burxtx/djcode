from django.conf.urls.defaults import patterns, include, url
from bloghub.blog.views import *
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import os.path
from django.views.generic import FormView
from blog.forms import BlogPostSaveForm
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

# site_media = os.path.join(os.path.dirname(__file__), 'site_media').replace('\\', '/')
# site_media = "C:/djcode/bloghub/site_media"

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bloghub.views.home', name='home'),
    # url(r'^bloghub/', include('bloghub.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    # Browsing
    (r'^$', main_page),
    url(r'^user/(\w+)/$', user_page, name="user_page"),
    url(r'^user/(\w+)/draft/$', draft_page, name="draft_page"),
    (r'^tag/([^\s]+)/$', tag_page),
    # (r'^tag/$', tag_cloud_page),
    (r'^search/$', search_page),
    url(r'^blogpost/(\d+)/$', blogpost_detail_page, name="blogpost_detail"),
    url(r'^draft/(\d+)/$', draft_detail_page, name="draft_detail"),
    # Session management
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', name="login_page"),
    url(r'^accounts/logout/$', logout_page, name="logout_page"),
    # (r'^site_media/(?P<path>.*)$', 'django.views.static.server',
    #     { 'document_root':site_media }),
    # (r'^site_media/css/(?P<path>.*)$', 'django.views.static.server',
    #     { 'document_root':site_media + '/css/' }),
    # (r'^site_media/js/(?P<path>.*)$', 'django.views.static.server',
    #     { 'document_root':site_media + '/js/' }),
    # (r'^site_media/img/(?P<path>.*)$', 'django.views.static.server',
    #     { 'document_root':site_media + '/img/' }),               
    url(r'^register/$', register_page, name="register_page"),
    (r'^register/success/$', direct_to_template,
        { 'template': 'registration/register_success.html' }),
    # Account management
    url(r'^save/$', blogpost_save_page, name="blogpost_save"),
    url(r'^blogpost/edit/(\d+)/$', blogpost_save_page, name="blogpost_update"),
    url(r'^blogpost/delete/(\d+)/$', blogpost_delete, name="blogpost_delete"),
    # url(r'^blogpost/delete/$', blogpost_delete, name="blogpost_delete"),
    # if there is no parameters from security respect? 
    # url(r'^blogpost/edit/$', blogpost_save_page, name="blogpost_update"),
    # Friends
    (r'^following/(\w+)/$', friends_page),
    (r'^friend/add/$', friend_add),
    (r'^friend/remove/$', friend_remove),
    # django comments
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^ratings/', include('ratings.urls')),
    (r'^ajax/tag/autocomplete/$', ajax_tag_autocomplete),
    url(r'^$', FormView.as_view(
        template_name="blogpost_detail.html",
        form_class=BlogPostSaveForm)),
)
urlpatterns += staticfiles_urlpatterns()