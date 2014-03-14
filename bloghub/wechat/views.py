# Create your views here.
# coding: utf-8
import hashlib
from datetime import datetime
import pdb, time, re
import xml.etree.ElementTree as ET
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode
from wechat.models import *

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.template import RequestContext
from django.utils import simplejson
from ratings.handlers import ratings, RatingHandler
from ratings.forms import StarVoteForm, SliderVoteForm
from ratings.models import Vote
from django.core.urlresolvers import reverse
from blog.models import *

ratings.register(Product, form_class=StarVoteForm)
#pdb.set_trace()
kwd = {
    'main_menu' : "M",
    'start' : "##",
    'restart' : 'R',
    'buy' : '0',
    'sell' : '1',
    'view' : '2',
    'delete' : '3',
    'reset' : '*',
}
note = {
    'main_menu' : "To start pls input: \
                   [%s]Start to search products or to publish a sale\
                   [%s]Restart a buy or sell event\
                   [%s]View your on sale"
                    % (kwd['start'], kwd['restart'], kwd['view']),
    'buy_sell' : "Input: [%s]Buy [%s]Sell [%s]Reset" % (kwd['buy'], kwd['sell'], kwd['reset']),
    'product' : "Input product name",
    'location' : "Send your location",
    'photo' : "Send product photo",
    'price' : "Send product price",
    'desc' : "Send product description",
    'search' : 'Matching product...',
}
query_set={}

# def get_access_token():
def checkSignature(request):
    signature=request.GET.get('signature',None)
    timestamp=request.GET.get('timestamp',None)
    nonce=request.GET.get('nonce',None)
    echostr=request.GET.get('echostr',None)
    token='ettian'

    tmplist=[token,timestamp,nonce]
    tmplist.sort()
    tmpstr="%s%s%s"%tuple(tmplist)
    tmpstr=hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echostr
    else:
        return None

def bind_wechat(request):
    if request.method == 'POST':
        if request.session.has_key('openid') and request.session['openid'] == request.GET.get('openid', None):
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    wechatuser, created = WechatUser.objects.get_or_create(openid=request.session['openid'], user=user)
                    if created:
                        # Redirect to a success page.
                        return HttpResponse('WeChat user is binded to Hashky successfully!')
                    else:
                        return HttpResponse('WeChat user is already binded to a Hashky user')
                else:
                    # Return a 'disabled account' error message
                    return HttpResponse('Disabled account!')
            else:
                # Return an 'invalid login' error message.
                return HttpResponse('Invalid login!')
        else:
            return HttpResponse('Bind exception: no openid in session! Please send the bind request again')
    else:
        signature=request.GET.get('signature', None)
        timestamp = request.GET.get('timestamp', None)
        openid = request.GET.get('openid', None)
        token = 'bindhashky'
        tmplist=[token,timestamp,openid]
        tmplist.sort()
        tmpstr="%s%s%s"%tuple(tmplist)
        tmpstr=hashlib.sha1(tmpstr).hexdigest()
        if tmpstr == signature:
            if time.time() - int(timestamp) <= 1800:
                # save openid to session
                # Thanks to http://abyssly.com/2013/09/20/wx_bind/
                if not request.session.get('openid', False):
                    # return HttpResponse('Openid is not presented')
                    request.session['openid'] = openid
                return render_to_response('registration/bind_wechat.html')
            else:
                return HttpResponse('Link expired, please send binding request again')
        else:
            return HttpResponse("Security warning, please check if your account is leaked, and send binding request from official site.")


@csrf_exempt
def index(request):
    if request.method=='GET':
        return HttpResponse(checkSignature(request))
    elif request.method=="POST":
        return HttpResponse(msg_response(request), content_type="application/xml")
    else:
        return None

def parse_raw_xml(root_elem):
    msg = {}
    if root_elem.tag == 'xml':
        for child in root_elem:
            msg[child.tag] = smart_str(child.text)
    return msg

def get_reply(msg, reply):
    text_tpl = '''
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[%s]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>'''
    reply_msg = text_tpl % (
        msg["FromUserName"],
        msg["ToUserName"],
        str(int(time.time())),
        'text',
        reply)
    return reply_msg

def get_reply_article(msg, reply):
    # reply search product result
    multimedia_tpl = '''
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[%s]]></MsgType>
    <ArticleCount>%s</ArticleCount>
    <Articles>
    '''
    item_tpl = '''
    <item>
    <Title><![CDATA[%(article_title)s]]></Title> 
    <Description><![CDATA[%(desc)s]]></Description>
    <PicUrl><![CDATA[%(picurl)s]]></PicUrl>
    <Url><![CDATA[%(url)s]]></Url>
    </item>'''
    close_tpl = '''
    </Articles>
    </xml>
    '''
    tpl_list = [multimedia_tpl]
    # biz goes here...
    for i in reply:
        item_tpl = item_tpl % i
        tpl_list.append(item_tpl)
    tpl_list.append(close_tpl)
    news_tpl = '\n'.join(tpl_list)
    reply_msg = news_tpl % (
        msg["FromUserName"],
        msg["ToUserName"],
        str(int(time.time())),
        'news',
        len(reply),)
    return reply_msg

def msg_response(request):
    # get request and parse raw xml
    raw_str = smart_str(request.raw_post_data)
    msg = parse_raw_xml(ET.fromstring(raw_str))
    # get text msg
    if msg['MsgType'] == 'event' and msg['Event'] == 'subscribe':
        # check if openid is already binded to system
        bind_link = ''
        token = 'bindhashky'
        openid = msg['FromUserName']
        timestamp = msg['CreateTime']
        tmplist=[token,timestamp,openid]
        tmplist.sort()
        tmpstr="%s%s%s"%tuple(tmplist)
        signature=hashlib.sha1(tmpstr).hexdigest()
        try:
            wechatuser = WechatUser.objects.get(openid=openid)
            if wechatuser.user == None:
                bind_link = '<a href="http://www.hashky.com/wechat/binding/?openid=%s&timestamp=%s&signature=%s">Please bind with Hashky account<a/>'\
                % (msg['openid'], timestamp, signature)
            else:
                return get_reply(msg, 'Welcome back!')
        except:
            bind_link = '<a href="http://www.hashky.com/wechat/binding/?openid=%s&timestamp=%s&signature=%s">Please bind with Hashky account<a/>'\
            % (openid, timestamp, signature)
        # send bind openid with system user request
        welcome = '''
        Hi, welcome to subscribe Hashky! To get a better service, please bind your WeChat account with Hashky account.
        '''
        return get_reply(msg, welcome+bind_link)
    elif msg['MsgType'] == 'event' and msg['Event'] == 'unsubscribe':
        goodbye = "Please don't leave me..."
        return get_reply(msg, goodbye)
    else:
        if msg['MsgType']=='text':
            query = msg.get('Content', 'You input nothing').strip()
        if msg['MsgType']=='location':
            query_x=msg.get('Location_X', 'You location is unknown')
            query_y=msg.get('Location_Y', 'You location is unknown')
            query_label=msg.get('Label', 'You location is unknown')
            query=(query_x,query_y,query_label)
        if msg['MsgType']=='image':
            query_picurl = msg.get('PicUrl', "You didn't send a product photo")
            query_mediaid = msg.get('MediaId', "You didn't send a product photo")
            query=(query_picurl, query_mediaid)
        return query_photo(msg, query)

def query_action(msg, query):
    # if buy or sell
    global query_set
    user = msg['FromUserName']
    if query == kwd['buy'] or query == kwd['sell']:
        query_set[user] = {}
        query_set[user]['action'] = query
        reply = note['product']
    #     # query db should start here
    #     return 
    else:
        reply = note['buy_sell']
    print query_set
    return get_reply(msg, reply)

def query_product(msg,query):
    global query_set
    user = msg['FromUserName']
    if query_set.has_key(user) and query_set[user].has_key('action'):
        #if product
        if type(query) is str:
            query_set[user]['product']=query
            reply = note['desc']
        else:
            reply = note['product']
    else:
        return query_action(msg,query)
    print query_set
    return get_reply(msg,reply)

def query_desc(msg, query):
    global query_set
    user = msg['FromUserName']
    if query_set.has_key(user) and query_set[user].has_key('product'):
        if type(query) is str:
            query_set[user]['desc']=query
            reply = note['price']
        else:
            reply = note['desc']
    else:
        return query_product(msg,query)
    print query_set
    return get_reply(msg,reply)

def query_price(msg,query):
    global query_set
    user = msg['FromUserName']
    if query_set.has_key(user) and query_set[user].has_key('desc'):
        try:
            query = int(query)
            query_set[user]['price']=query
            reply = note['location']
        except:
            reply = note['price']
    else:
        return query_desc(msg,query)
    print query_set
    return get_reply(msg,reply)

def query_location(msg, query):
    global query_set
    user = msg['FromUserName']
    if query_set.has_key(user) and query_set[user].has_key('price'):
        if msg['MsgType']=='location':
            query_set[user]['location']=query
            # if action is buy, terminate the process at send location step
            if query_set[user]['action'] != kwd['buy']:
                reply = note['photo']
            else:
                # reply = note['search']
                # enter db operate
                print query_set, 'one item is done!'
                product_db_write(msg)
                reply = product_db_query(msg)
                query_set[user] = {}
                # return write_read_query_reply(msg, query)
                if isinstance(reply, list):
                    return get_reply_article(msg, reply)
                else:
                    return get_reply(msg, reply)
        else:
            reply = note['location']
    else:
        return query_price(msg,query)
    print query_set
    return get_reply(msg,reply)

def query_photo(msg, query):
    global query_set
    user = msg['FromUserName']
    if query == kwd['reset']:
        reply = note['buy_sell']
        # if not query_set.has_key[user] or query_set[user] != {}:
        query_set[user]={}
    else:
        if query_set.has_key(user) and query_set[user].has_key('location'):
            if msg['MsgType'] == 'image':
                query_set[user]['photo'] = query
                # reply = note['search']
                # enter db operate
                print query_set, 'one item is done!'
                # write db, query db, reply a media text
                product_db_write(msg)
                reply = product_db_query(msg)
                query_set[user] = {}
                # return write_read_query_reply(msg, query)
                if isinstance(reply, list):
                    return get_reply_article(msg, reply)
                else:
                    return get_reply(msg, reply)
            else:
                reply = note['photo']
        else:
            return query_location(msg,query)
    print query_set
    return get_reply(msg, reply)

def product_db_query(msg):
    # TODO: Calculate the nearest product
    # now only return one product for test
    query_user = msg['FromUserName']
    reply = []
    if query_set[query_user]['action'] == kwd['buy']:
        action = kwd['sell']
    else:
        action = kwd['buy']
    query_wechatuser= WechatUser.objects.select_related().get(openid=query_user)
    products = Product.objects.filter(
        name__icontains=query_set[query_user]['product'],
        status=action
        ).exclude(user=query_wechatuser.id)
    if len(products) >= 1:
        # Tencent defines that max article count is 10.
        # http://mp.weixin.qq.com/wiki/index.php?title=%E5%8F%91%E9%80%81%E8%A2%AB%E5%8A%A8%E5%93%8D%E5%BA%94%E6%B6%88%E6%81%AF#.E5.9B.9E.E5.A4.8D.E5.9B.BE.E6.96.87.E6.B6.88.E6.81.AF
        for product in products[:10]:
            item = {}
            article_user = product.user.user
            article_title = product.name
            article_price = product.price
            article_desc = product.desc
            article_body = '''Following products are found for you:
            Name: %s
            Desc: %s
            Price: %s
            Owner: %s
            ''' % (article_title, article_desc, article_price, article_user)
            if action == kwd['sell']:
                photo = Photo.objects.filter(pk=product.id)
                if len(photo) != 0:
                    article_picurl = photo[0].picurl
                else:
                    article_picurl = "http://www.hashky.com/wechat/dummy/"
                article_url = "http://www.hashky.com/wechat/product/%s/" % product.id
                item['article_title'] = article_title
                item['desc'] = article_body
                item['picurl'] = article_picurl
                item['url'] = article_url
                reply.append(item)
            if action == kwd['buy']:
                # photo = Photo.objects.filter(pk=product.id)
                # if len(photo) != 0:
                #     article_picurl = photo[0].picurl
                # else:
                #     article_picurl = "http://www.hashky.com/dummy/"
                article_picurl = "http://www.hashky.com/wechat/dummy/"
                article_url = "http://www.hashky.com/wechat/product/%s/" % product.id
                item['article_title'] = article_title
                item['desc'] = article_body
                item['picurl'] = article_picurl
                item['url'] = article_url
                reply.append(item)
        return reply
    else:
        return "No proper product found, try another product name"
# TODO: Moderation is needed before write user input to db
def product_db_write(msg):
    user = msg['FromUserName']
    #convert POSIX timestamp to datetime obj
    create_time = datetime.fromtimestamp(int(msg['CreateTime']))
    prd_name = query_set[user]['product']
    prd_price = query_set[user]['price']
    wechatuser, created = WechatUser.objects.get_or_create(openid=user)
    product = Product.objects.create(user_id=wechatuser.id, 
        name=prd_name,
        price=prd_price,
        timestamp=create_time,
        desc=query_set[user]['desc'],
        status=query_set[user]['action'],
        )
    
    loc = Location.objects.create(product_id=product.id, 
        x=query_set[user]['location'][0],
        y=query_set[user]['location'][1],
        label=query_set[user]['location'][2])
    if query_set[user]['action'] == kwd['sell'] and query_set[user].has_key('photo'):
        # picurl = msg['PicUrl']
        # mediaid = msg['MediaId']
        photo = Photo.objects.create(
            product_id=product.id,
            picurl=query_set[user]['photo'][0], 
            mediaid=query_set[user]['photo'][1],
            )
        product.photo_set.add(photo)
    # if picurl not found or mediaid not exist, define dummy picurl and mediaid
    # else:
    #     picurl = ''
    #     mediaid = ''
    # photo = Photo.objects.create(
    #     product_id=product.id,
    #     picurl=query_set[user]['photo'][0], 
    #     mediaid=query_set[user]['photo'][1],
    #     )
    # product.photo_set.add(photo)

def product_detail(request, product_id):
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=product_id)
        if product:
            # cannot use _set query, because user and blogpost is not manytomany relationship
            # username = blogpost.user_set.all().values("username")[0]["username"]
            username = product.user.user
        variables = RequestContext(request,{
            'product': product,
            # rename template variable to reuse rating and comment apps
            'object': product,
            # 'show_tags': True,
            # 'show_body': True,
            'show_edit': username==request.user.username,
            })
        return render_to_response('product_detail.html', variables)

def product_page(request, username):
    user = get_object_or_404(User, username=username)
    # blogposts = user.blogpost_set.order_by('-id')
    wechatuser, created = WechatUser.objects.get_or_create(user=user.id)
    products = Product.objects.get_or_create(status='0', user=wechatuser.id)
    if request.user.is_authenticated():
        is_following = Followingship.objects.filter(
            following=request.user,
            followers=user)
    else:
        is_following = False
    variables = RequestContext(request, {
        'username':username,
        'products':products,
        # 'show_tags': True,
        'show_body': True,
        # 'show_edit': username==request.user.username,
        'is_following': is_following,
        })
    return render_to_response('product_page.html', variables)

def product_main_page(request):
    user = request.user
    # latest avtivities from following people
    following_people = [followingship.followers for followingship in user.following_set.all()]
    following_people_blogposts = BlogPost.objects.filter(
        user__in=following_people,
        status=BlogPost.LIVE_STATUS,
        ).order_by('-id')
    variables = RequestContext(request, {
        'username': user,
        'following_people': following_people,
        'blogposts': following_people_blogposts,
        # 'show_tags': True,
        'show_user': True,
        'show_body': True,
        # 'tags': tags,
        })
    return render_to_response('product_main_page.html', variables)
