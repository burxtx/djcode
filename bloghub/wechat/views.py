# Create your views here.
# coding: utf-8
from django.http import HttpResponse
import hashlib
import pdb
import xml.etree.ElementTree as ET
import time
#pdb.set_trace()
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

def msg_response(request):
    # get request and parse raw xml
    raw_str = smart_str(request.raw_post_data)
    msg = parse_raw_xml(ET.fromstring(raw_str))
    # get text msg
    q_text = msg.get('Content', 'You input nothing')
    test_reply = q_text
    return get_reply(msg, test_reply)
