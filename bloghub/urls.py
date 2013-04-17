from django.conf.urls.defaults import patterns, include, url
from bloghub.blog.views import *
from django.views.generic.simple import direct_to_template
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import os.path
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
    (r'^user/(\w+)/$', user_page),
    (r'^tag/([^\s]+)/$', tag_page),
    # (r'^tag/$', tag_cloud_page),
    (r'^search/$', search_page),
    url(r'^blogpost/(\d+)/$', blogpost_detail_page, name="blogpost_detail"),
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
    # Friends
    (r'^following/(\w+)/$', friends_page),
    (r'^friend/add/$', friend_add),
    # django comments
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^ratings/', include('ratings.urls')),
)
urlpatterns += staticfiles_urlpatterns()