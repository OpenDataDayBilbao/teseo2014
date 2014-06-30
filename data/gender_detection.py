# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 09:18:11 2014

@author: aitor
"""

import urllib2
import json

def get_gender(name):
    req = urllib2.Request("http://www.i-gender.com/ai", "name=%s" % (name))
    resp = urllib2.urlopen(req).read()
    decoder = json.JSONDecoder()
    result = decoder.decode(resp)
    return result['gender'], result['confidence']  
    
