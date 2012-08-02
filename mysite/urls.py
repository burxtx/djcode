from django.conf.urls.defaults import patterns, include, url
from mysite.views import hello,current_datetime,hours_ahead
from django.contrib import admin
from mysite.books import views
admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
#    ('^$', homepage),
    ('^time/plus/(\d{1,2})/$', hours_ahead),
    ('^time/$', current_datetime),
    ('^hello/$', hello),
    (r'^search-form/$', views.search_form),
    (r'^search/$', views.search),
    url(r'^blog/', include('mysite.blog.urls')),
)
