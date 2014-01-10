# Create your views here.
# coding: utf-8
from django.http import HttpResponse
import hashlib
def checkSignature(request):
    '''
      验证微信api提供的signature和token等信息  
    '''
    
    token = 'ettian'
    signature = request.GET.get('signature', '')
    timestamp = request.GET.get('timestamp', '')
    nonce = request.GET.get('nonce',  '')
    echostr = request.GET.get('echostr', '')
    
    infostr = ''.join(sorted([token, timestamp, nonce]))
    if infostr:
        hashstr = hashlib.sha1(infostr).hexdigest()
        if hashstr is signature:
            return HttpResponse(echostr)
        else:
            print 'haststr is not signature'
    else:
        print 'infostr does not existing'