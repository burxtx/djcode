# Create your views here.
# coding: utf-8
from django.http import HttpResponse
import hashlib
import pdb, time, re
import xml.etree.ElementTree as ET
#pdb.set_trace()
kwd = {
    'main_menu' : "M",
    'start' : "##",
    'restart' : 'R',
    'buy' : '0',
    'sell' : '1',
    'view' : '2',
    'delete' : '3',
    'reset' : '4',
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

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def index(request):
    if request.method=='GET':
        return HttpResponse(checkSignature(request))
    elif request.method=="POST":
        return HttpResponse(msg_response(request), content_type="application/xml")
    else:
        return None

from django.utils.encoding import smart_str, smart_unicode
def parse_raw_xml(root_elem):
    msg = {}
    if root_elem.tag == 'xml':
        for child in root_elem:
            msg[child.tag] = smart_str(child.text)
    return msg

def get_reply(msg, reply):
    text_tpl = "\
    <xml>\
    <ToUserName><![CDATA[%s]]></ToUserName>\
    <FromUserName><![CDATA[%s]]></FromUserName>\
    <CreateTime>%s</CreateTime>\
    <MsgType><![CDATA[%s]]></MsgType>\
    <Content><![CDATA[%s]]></Content>\
    </xml>"
    reply_msg = text_tpl % (
        msg["FromUserName"],
        msg["ToUserName"],
        str(int(time.time())),
        'text',
        reply)
    return reply_msg

def reply_result(msg, reply):
    # reply search product result
    pass

def msg_response(request):
    # get request and parse raw xml
    raw_str = smart_str(request.raw_post_data)
    msg = parse_raw_xml(ET.fromstring(raw_str))
    # get text msg
    if msg['MsgType']=='text':
        query = msg.get('Content', 'You input nothing').strip()
    if msg['MsgType']=='location':
        query_x=msg.get('Location_X', 'You location is unknown')
        query_y=msg.get('Location_Y', 'You location is unknown')
        query=(query_x,query_y)
    if msg['MsgType']=='image':
        query_picurl = msg.get('PicUrl', "You didn't send a product photo")
        query_mediaid = msg.get('MediaId', "You didn't send a product photo")
        query=(query_picurl, query_mediaid)
    return query_location(msg, query)

def query_action(msg, query):
    # if buy or sell
    global query_set
    if query == kwd['buy'] or query == kwd['sell']:
        query_set['action'] = query
        reply = note['product']
    #     # query db should start here
    #     return 
    else:
        reply = note['buy_sell']
    print query_set
    return get_reply(msg, reply)

def query_product(msg,query):
    global query_set
    if query_set.has_key('action'):
        #if product
        if type(query) is str:
            query_set['product']=query
            reply = note['desc']
        else:
            reply = note['product']
    else:
        return query_action(msg,query)
    print query_set
    return get_reply(msg,reply)

def query_desc(msg, query):
    global query_set
    if query_set.has_key('product'):
        if type(query) is str:
            query_set['desc']=query
            reply = note['price']
        else:
            reply = note['desc']
    else:
        return query_product(msg,query)
    print query_set
    return get_reply(msg,reply)

def query_price(msg,query):
    global query_set
    if query_set.has_key('desc'):
        # pattern = re.compile('[0-9]+')
        # match = pattern.match(query)
        try:
            query = int(query)
            query_set['price']=query
            reply = note['location']
        except:
            reply = note['price']
    else:
        return query_desc(msg,query)
    print query_set
    return get_reply(msg,reply)

def query_location(msg, query):
    global query_set
    if query == kwd['reset']:
        reply = note['buy_sell']
        if query_set != {}:
            query_set={}
    else:
        if query_set.has_key('price'):
            # if location
            if msg['MsgType']=='location':
                query_set['location']=query
                reply = note['search']
                #enter db operate
                print query_set, 'one item is done!'
                reply_result(msg,'a reply')
                query_set = {}
            else:
                reply = note['location']
        
        else:
            return query_price(msg,query)
    print query_set
    return get_reply(msg,reply)

# from wechat.models import *
# def buy_product(query, query_set):
#     product = Product.objects.filter(title__icontains=query)[:3]

# def action_index(query, query_set, msg):
#     if query_set['action'] == '0':
#         return buy_product(query, query_set)
#     if query_set['action'] == '1':
#         return sell_product(query, query_set)
# def sell_product(request, msg):
#     product, created = Product.objects.get_or_create(user=)
#     product.name = msg["FromUserName"]
#     product.desc = desc_reply
#     product.timestamp = str(int(time.time()))
#     product.locationX = msg[]
