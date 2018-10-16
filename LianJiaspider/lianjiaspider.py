#!usr/bin/env python
# _*_ coding:utf-8 _*_
import re
import urllib2
import mysql.connector
import random
import threading
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import lianjialogin


regions = [u"pudong", u"minhang", u"baoshan", u"xuhui", u"putuo", u"yangpu", u"changning", u"songjiang", u"jiading", u"huangpu", u"jingan", u"zhabei", u"hongkou", u"qingpu", u"fengxian", u"jinshan", u"chongming", u"shanghaizhoubian"]
lock = threading.Lock()


def load_user_agents(uafile):
	uas = []
	with open(uafile, 'rb') as uaf:
		for ua in uaf.readlines():
			if ua:
				uas.append(ua.strip()[1:-1])  # 去掉“”
	random.shuffle(uas)  # 随机排序
	return uas


uas = load_user_agents("user_agents.txt")


class mysql_wraper(object):
	def __init__(self, command=''):
		self.lock = threading.RLock()
		if command != '':
			conn = self.get_conn()
			cu = conn.cursor()
			cu.execute(command)

	def get_conn(self):
		conn = mysql.connector.connect(user='lianjia', password='lianjia', database='lianjia', host='127.0.0.1',
	                               port=3306, use_unicode=True, charset='utf8', collation='utf8_general_ci',
	                               autocommit=False)
		return conn

	def conn_close(self, conn=None):
		conn.close()

	def conn_trans(func):
		def connection(self, *args, **kw):
			self.lock.acquire()
			conn = self.get_conn()
			kw['conn'] = conn
			rs = func(self, *args, **kw)
			self.conn_close(conn)
			self.lock.release()
			return rs
		return connection

	@conn_trans
	def execute(self, comand, method_flag=0, conn=None):
		cu = conn.cursor()
		try:
			if not method_flag:
				cu.execute(comand)
			else:
				cu.execute(comand[0],comand[1])
			conn.commit()
		except Exception, e:
			print e
			return -2
		return 0

	@conn_trans
	def fetchall(self, comand="select name from xiaoqu", conn=None):
		cu = conn.cursor()
		lists = []
		try:
			cu.execute(comand)
			lists = cu.fetchall()
		except Exception, e:
			print e
			pass
		return lists


def gen_xiaoqu_insert_command(info_dict):
	info_list = [u'小区名称', u'小区链接', u'大区域', u'小区域', u'建造时间']
	t = []
	for il in info_list:
		if il in info_dict:
			t.append(info_dict[il])
		else:
			t.append('')
	t = tuple(t)
	command = (r"insert into xiaoqu values(?,?,?,?,?)", t)
	return command


def gen_chengjiao_insert_comand(info_dict):
	info_list = [u'链接', u'小区名称', u'户型', u'面积', u'朝向', u'楼层', u'建造时间', u'签约时间', u'签约单价', u'签约总价', u'房产类型', u'学区', u'地铁']
	t = []
	for il in info_list:
		if il in info_dict:
			t.append(info_dict[il])
		else:
			t.append('')
	t.tuple(t)
	command = (r"insert into chengjiao values(?,?,?,?,?,?,?,?,?,?,?,?,?)", t)
	return command


def xiaoqu_spider(db_xq, url_page=u"https://sh.lianjia.com/xiaoqu/pg1rs/"):
	try:
		head = {'User-Agent': random.choice(uas)}
		req = urllib2.Request(url_page, headers=head)
		source_code = urllib2.urlopen(req, timeout=10).read()
		plain_text = unicode(source_code)
		soup = BeautifulSoup(plain_text)
	except (urllib2.HTTPError, urllib2.URLError), e:
		print e
		exit(-1)
	except Exception,e:
		print e
		exit(-1)
	xiaoqu_list = soup.findAll('div', {'class': 'info'})
	for xq in xiaoqu_list:
		info_dict = {}
		info_dict.update({u'小区名称': xq.find('div', {'class': 'title'}).a.text})
		info_dict.update({u'小区链接': xq.find('div', {'class': 'title'}).a.get('href')})
		info_dict.update({u'大区域': xq.find('a', {'class': 'district'}).text})
		info_dict.update({u'小区域': xq.find('a', {'class': 'bizcircle'}).text})
		info_dict.update({u'建造时间': xq.find('div', {'class': 'positionInfo'}).text})
		command = gen_xiaoqu_insert_command(info_dict)
		db_xq.execute(command, 1)


def do_xiaoqu_spider(db_xq, region=u"浦东"):
	url = u"https://sh.lianjia.com/xiaoqu/" + region + "/"
	try:
		head = {'User-Agent': random.choice(uas)}
		req = urllib2.Request(url, headers=head)
		source_code = urllib2.urlopen(req, timeout=5).read()
		plain_text = unicode(source_code)
		soup = BeautifulSoup(plain_text)
	except (urllib2.HTTPError, urllib2.URLError), e:
		print e
		return
	except Exception, e:
		print e
		return
	totaldiv = soup.find('h2', {'class': 'total fl'})
	total = totaldiv.span.text
	total_page = int(total)/30 + 1  # 一页30条数据
	threads = []
	for i in xrange(total_page):
		url_page = u"https://sh.lianjia.com/xiaoqu/%s/pg%d/" % (region, i)
		t = threading.Thread(target=xiaoqu_spider, args=(db_xq, url_page))
		threads.append(t)
		t.start()
		t.join()
	# for t in threads:
	# 	t.start()
	# for t in threads:
	# 	t.join()
	print u"获取了%s 区所有的小区信息共%s条" % (region, total)


if __name__ == "__main__":
	conn = mysql_wraper()
	for region in regions:
		do_xiaoqu_spider(conn, region)
