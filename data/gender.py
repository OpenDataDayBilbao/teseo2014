# -*- coding: utf-8 -*-
"""
https://github.com/block8437/gender.py
"""

import requests, json

def getGenders(names):
	url = ""
	cnt = 0
	for name in names:
		if url == "":
			url = "name[0]=" + name
		else:
			url = url + "&name[" + str(cnt) + "]=" + name
		cnt += 1

  
	req = requests.get("http://api.genderize.io?" + url)
	results = json.loads(req.text)
	
	retrn = []
	for result in results:
		if result["gender"] != None:
			retrn.append((result['name'], result["gender"], result["probability"], result["count"]))
		else:
			retrn.append((u'None',u'0.0',0.0))
	return retrn
 
