#!usr/bin/env python
# _*_ coding:utf-8 _*_


import json
import random
import sys
import requests
import time
import urllib2
import mysql.connector
from multiprocessing.dummy import Pool as ThreadPool


reload(sys)
urls = []


def LoadUserAgents(uafile):
	uas = []
	with open(uafile, 'rb') as uaf:
		for ua in uaf.readlines():
			if ua:
				uas.append(ua.strip()[1:-1])
	random.shuffle(uas)
	return uas


uas = LoadUserAgents("user_agents.txt")
for m in range(2449072, 2449073):
	for i in range(m*100, (m+1)*100):
		url = 'https://space.bilibili.com/' + str(i)
		urls.append(url)


def getsource(url):
	payload = {
		'mid': url.replace('https://space.bilibili.com/', ''),
		'csrf': ''
	}
	ua = random.choice(uas)
	head = {
		'User-Agent': ua,
		'Referer': url + '/'
	}
	# req = urllib2.Request('https://space.bilibili.com/ajax/member/GetInfo', headers=head, data=payload)
	# jsontxt = urllib2.urlopen(req).read()
	jsontxt = requests.session().post('https://space.bilibili.com/ajax/member/GetInfo', headers=head, data=payload).text
	timenow = time.time()
	try:
		jsdic = json.loads(jsontxt)
		statusjson = jsdic['status'] if 'status' in jsdic.keys() else False
		if statusjson:
			if 'data' in jsdic.keys():
				jsdata = jsdic['data']
				mid = jsdata['mid']
				name = jsdata['name']
				sex = jsdata['sex']
				rank = jsdata['rank']
				face = jsdata['face']
				regtimestamp = jsdata['regtime'] if 'regtime' in jsdata.keys() else 0  # 部分用户没有提供注册时间
				regtime_local = time.localtime(regtimestamp)
				regtime = time.strftime("%Y-%m-%d %H:%M:%S", regtime_local)
				spacesta = jsdata['spacesta']
				birthday = jsdata['birthday'] if 'birthday' in jsdata.keys() else 'nobirthday'
				sign = jsdata['sign']
				level = jsdata['level_info']['current_level']
				officialverifytype = jsdata['official_verify']['type']
				officialverifydesc = jsdata['official_verify']['desc']
				viptype = jsdata['vip']['vipType']
				vipstatus = jsdata['vip']['vipStatus']
				toutu = jsdata['toutu']
				toutuid = jsdata['toutuId']
				coins = jsdata['coins']
				print("succeed get user info:" + str(mid) + "\t" + str(timenow))
				try:
					res = requests.get('https://api.bilibili.com/x/relation/stat?vmid=' + str(mid) + '&jsonp=jsonp').text
					# viewinfo = requests.get('https://api.bilibili.com/x/space/upstat?mid=' + str(mid) + '&jsonp=jsonp&callback=__jp5').text
					urlview = 'https://api.bilibili.com/x/space/upstat?mid=' + str(mid) + '&jsonp=jsonp'
					req = urllib2.Request(urlview, headers=head)
					viewinfo = urllib2.urlopen(req).read()
					js_fans_data = json.loads(res)
					js_view_data = json.loads(viewinfo)
					following = js_fans_data['data']['following']
					fans = js_fans_data['data']['follower']
					archiveview = js_view_data['data']['archive']['view']
					article = js_view_data['data']['article']['view']
				except Exception as e:
					print e
					following = 0
					fans = 0
					archiveview = 0
					article = 0
			else:
				print ('no data')
			try:
				conn = mysql.connector.connect(user='bilibili', password='bilibili', database='bilibili', host='127.0.0.1', port=3306, use_unicode=True, charset='utf8', collation='utf8_general_ci', autocommit=False)
				cursor = conn.cursor()
				cursor.execute('INSERT INTO bilibili_user_info(mid, name, sex, rank, face, regtime, spacesta, \
				birthday, sign, level, OfficialVerifyType, OfficialVerifyDesc, vipType, vipStatus, \
				toutu, toutuId, coins, following, fans, archiveview, article) \
				VALUES("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", \
				"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' %
				               (mid, name, sex, rank, face, regtime, spacesta, birthday, sign, level, \
				                officialverifytype, officialverifydesc, viptype, vipstatus, toutu, toutuid, coins, \
				                following, fans, archiveview, article))
				conn.commit()
			except Exception as e:
				print e
		else:
			print('error:' + url)
	except Exception as e:
		print e
		pass


if __name__ == '__main__':
	pool = ThreadPool(1)
	try:
		results = pool.map(getsource, urls)
	except Exception as e:
		print(e)
	pool.close()
	pool.join()


