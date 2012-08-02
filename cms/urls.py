from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from cms.search.views import search
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cms.views.home', name='home'),
    # url(r'^cms/', include('cms.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'', include('django.contrib.flatpages.urls')),
    ('^tiny_mce/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root':'media'}),
    (r'^search/$', 'search'),
    (r'^weblog/$', 'coltrane.views.entries_index'),
)
