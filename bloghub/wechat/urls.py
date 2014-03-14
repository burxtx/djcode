from django.conf.urls.defaults import patterns, include, url

urlpatterns=patterns('',
    url(r'^$','wechat.views.index'),
    # url(r'^product//$','wechat.views.product_list'),
    url(r'^product/(\d+)/$','wechat.views.product_detail'),
    url(r'^binding/$', 'wechat.views.bind_wechat'),
    url(r'^product/(\w+)/$', 'wechat.views.product_page'),
    url(r'^product/$', 'wechat.views.product_main_page')
)

