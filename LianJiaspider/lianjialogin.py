#!usr/bin/env python
# _*_ coding:utf-8 _*_
import urllib
import urllib2
import cookielib
import re
import zlib

cookie = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
urllib2.install_opener(opener)


home_url = 'http://sh.lianjia.com/'
auth_url = 'https://passport.lianjia.com/cas/login?service=http%3A%2F%2Fsh.lianjia.com%2F'
chengjiao_url = 'http://sh.lianjia.com/chengjiao/'


headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate, sdch',
	'Accept-Language': 'zh-CN,zh;q=0.8',
	'Cache-Control': 'no-cache',
	'Connection': 'keep-alive',
	'Content-Type': 'application/x-www-form-urlencoded',
	'Host': 'passport.lianjia.com',
	'Pragma': 'no-cache',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
}


req = urllib2.Request(home_url)
opener.open(req)
req = urllib2.Request(auth_url, headers=headers)
result = opener.open(req)


pattern = re.compile(r'JSESSIONID=(.*)')
jsessionid = pattern.findall(result.info().getheader('Set-Cookie').split(';')[0])[0]


html_content = result.read()
gzipped = result.info().getheader('Content-Encoding')
if gzipped:
	html_content = zlib.decompress(html_content, 16 + zlib.MAX_WBITS)
pattern = re.compile(r'value=\"(LT-.*)\"')
lt = pattern.findall(html_content)[0]
pattern = re.compile(r'name="execution" value="(.*)"')
execution = pattern.findall(html_content)[0]
data = {
	'username': '**********',
	'password': '**********',
	'execution': execution,
	'_eventId': 'submit',
	'lt': lt,
	'verifyCode': '',
	'redirect': ''
}
post_data = urllib.urlencode(data)
headers = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.8',
	'Cache-Control': 'no-cache',
	'Connection': 'keep-alive',
	'Content-Type': 'application/x-www-form-urlencoded',
	'Host': 'passport.lianjia.com',
	'Origin': 'https://passport.lianjia.com',
	'Pragma': 'no-cache',
	'Upgrade-Insecure-Requests': '1',
	'Referer': auth_url,
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
	'X-Requested-With': 'XMLHttpRequest'
}
req = urllib2.Request(auth_url, post_data, headers)
try:
	result = opener.open(req)
except urllib2.HTTPError, e:
	print e.getcode()
	print e.reason
	print e.geturl()
	print e.info()
	req = urllib2.Request(e.geturl())
	result = opener.open(req)
	req = urllib2.Request(chengjiao_url)
	result = opener.open(req).read()
