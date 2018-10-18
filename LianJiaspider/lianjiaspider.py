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
# import lianjialogin  # sh无论登陆与否都不会在列表中显示30内的成交价格


regions = ["pudong", "minhang", "baoshan", "xuhui", "putuo", "yangpu", "changning", "songjiang", "jiading", "huangpu", "jingan", "zhabei", "hongkou", "qingpu", "fengxian", "jinshan", "chongming", "shanghaizhoubian"]
regionname = ["浦东", "闵行", "宝山", "徐汇", "普陀", "杨浦", "长宁", "松江", "嘉定", "黄埔", "静安", "闸北", "虹口", "青浦", "奉贤", "金山", "崇明", "上海周边"]
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
				cu.execute(comand[0], comand[1])
			conn.commit()
		except Exception, e:
			print e
			return -2
		return 0

	@conn_trans
	def fetchall(self, comand="select url from xiaoqu where region=%s", conn=None, region='浦东'):
		cu = conn.cursor()
		lists = []
		try:
			cu.execute(comand, (region, ))
			lists = cu.fetchall()
		except Exception, e:
			print e
			pass
		return lists


def gen_xiaoqu_insert_command(info_dict):
	info_list = ['小区名称', '小区链接', '大区域', '小区域', '建造时间']
	t = []
	for il in info_list:
		if il in info_dict:
			t.append(info_dict[il])
		else:
			t.append('')
	t = tuple(t)
	command = (r"insert into xiaoqu values(%s,%s,%s,%s,%s)", t)
	return command


def gen_chengjiao_insert_command(info_dict):
	info_list = ['链接', '小区名称', '户型', '面积', '朝向', '楼层', '建造时间', '签约时间', '签约单价', '签约总价', '房产类型', '学区', '地铁', '装修', '电梯', '挂牌']
	t = []
	for il in info_list:
		if il in info_dict:
			t.append(info_dict[il])
		else:
			t.append('')
	t = tuple(t)
	command = (r"insert into chengjiao values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", t)
	return command


def xiaoqu_spider(db_xq, url_page="https://sh.lianjia.com/xiaoqu/pg1rs/"):
	try:
		head = {'User-Agent': random.choice(uas)}
		req = urllib2.Request(url_page, headers=head)
		source_code = urllib2.urlopen(req, timeout=10).read()
		soup = BeautifulSoup(source_code)
	except (urllib2.HTTPError, urllib2.URLError), e:
		print e
		exit(-1)
	except Exception, e:
		print e
		exit(-1)
	xiaoqu_list = soup.findAll('div', {'class': 'info'})
	for xq in xiaoqu_list:
		info_dict = {}
		info_dict.update({'小区名称': xq.find('div', {'class': 'title'}).a.text})
		info_dict.update({'小区链接': xq.find('div', {'class': 'title'}).a.get('href')})
		info_dict.update({'大区域': xq.find('a', {'class': 'district'}).text})
		info_dict.update({'小区域': xq.find('a', {'class': 'bizcircle'}).text})
		position = xq.find('div', {'class': 'positionInfo'}).text
		info_dict.update({'建造时间': position.split('/')[1]})
		command = gen_xiaoqu_insert_command(info_dict)
		db_xq.execute(command, 1)


def do_xiaoqu_spider(db_xq, region="pudong"):
	url = "https://sh.lianjia.com/xiaoqu/" + region + "/"
	try:
		head = {'User-Agent': random.choice(uas)}
		req = urllib2.Request(url, headers=head)
		source_code = urllib2.urlopen(req, timeout=5).read()
		soup = BeautifulSoup(source_code)
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
		url_page = "https://sh.lianjia.com/xiaoqu/%s/pg%d/" % (region, i)
		t = threading.Thread(target=xiaoqu_spider, args=(db_xq, url_page))
		threads.append(t)
		t.start()
		t.join()
	# for t in threads:
	# 	t.start()
	# for t in threads:
	# 	t.join()
	print "获取了%s 区所有的小区信息共%s条" % (region, total)


def chengjiao_spider(db_cj, url_page="https://sh.lianjia.com/xiaoqu/pg1rs/"):
	try:
		head = {'User-Agent': random.choice(uas)}
		req = urllib2.Request(url_page, headers=head)
		source_code = urllib2.urlopen(req, timeout=10).read()
		soup = BeautifulSoup(source_code)
	except (urllib2.HTTPError, urllib2.URLError), e:
		print e
		print url_page
		exception_write('chengjiao_spider', url_page)
		return
	except Exception, e:
		print e
		print url_page
		exception_write('chengjiao_spider', url_page)
		return
	cj_list = soup.findAll('div', {'class': 'info'})
	for cj in cj_list:
		info_dict = {}
		href = cj.find('a')
		if not href:
			continue
		info_dict.update({'链接': href.get('href')})
		info_dict.update({'小区名称': href.text.split()[0]})
		info_dict.update({'户型': href.text.split()[1]})
		info_dict.update({'面积': href.text.split()[2]})
		house_info = cj.find('div', {'class': 'houseInfo'}).text.strip().split('|')
		info_dict.update({'朝向': house_info[0]})
		info_dict.update({'装修': house_info[1]})
		if len(house_info) > 2:
			info_dict.update({'电梯': house_info[2]})
		price = cj.find('div', {'class': 'totalPrice'}).span.text
		if price.find('*') != -1:
			try:
				head = {'User-Agent': random.choice(uas)}
				req = urllib2.Request(href.get('href'), headers=head)
				source_code = urllib2.urlopen(req, timeout=10).read()
				soup1 = BeautifulSoup(source_code)
			except (urllib2.HTTPError, urllib2.URLError), e:
				print e
				print href.get('href')
				return
			except Exception, e:
				print e
				print href.get('href')
				return
			price1 = soup1.find('div', {'class': 'price'}).text.split('万')
			info_dict.update({'签约时间': soup1.find('div', {'class': 'house-title'}).div.span.text})
			info_dict.update({'签约总价': price1[0]})
			info_dict.update({'签约单价': price1[1]})
		else:
			info_dict.update({'签约时间': cj.find('div', {'class': 'dealDate'}).text})
			info_dict.update({'签约总价': cj.find('div', {'class': 'totalPrice'}).span.text})
			info_dict.update({'签约单价': cj.find('div', {'class': 'unitPrice'}).span.text})
		position_info = cj.find('div', {'class': 'positionInfo'}).text.split()
		info_dict.update({'楼层': position_info[0]})
		info_dict.update({'建造时间': position_info[1]})
		dealCycleTxt = cj.find('span', {'class': 'dealCycleTxt'})
		if dealCycleTxt:
			info_dict.update({'挂牌': dealCycleTxt.text.strip()})
		dealHouseTxt = cj.find('span', {'class': 'dealHouseTxt'})
		if dealHouseTxt:
			dealHouseTxt = dealHouseTxt.text.strip().split('/')
			for c in dealHouseTxt:
				if c.find('满') != -1:
					info_dict.update({'房产类型': c})
				elif c.find('学') != -1:
					info_dict.update({'学区': c})
				elif c.find('地铁') != -1:
					info_dict.update({'地铁': c})
		command = gen_chengjiao_insert_command(info_dict)
		db_cj.execute(command, 1)


def xiaoqu_chengjiao_spider(db_cj, xq_url='https://sh.lianjia.com/xiaoqu/5011063893329/'):
	url = 'https://sh.lianjia.com/chengjiao/c' + xq_url.split('xiaoqu/')[1]
	try:
		head = {'User-Agent': random.choice(uas)}
		req = urllib2.Request(url, headers=head)
		source_code = urllib2.urlopen(req, timeout=10).read()
		soup = BeautifulSoup(source_code)
	except (urllib2.HTTPError, urllib2.URLError), e:
		print e
		exception_write('xiaoqu_chengjiao_spider', xq_url)
		return
	except Exception, e:
		print e
		exception_write('xiaoqu_chengjiao_spider', xq_url)
		return
	totaldiv = soup.find('div', {'class': 'total fl'})
	total = totaldiv.span.text
	if total == '0':
		return
	total_page = int(total)/30 + 1  # 一页30条数据
	threads = []
	for i in xrange(total_page):
		url_page = url + 'pg%s/' % i
		t = threading.Thread(target=chengjiao_spider, args=(db_cj, url_page))
		threads.append(t)
		# t.start()
		# t.join()
	for t in threads:
		t.start()
	for t in threads:
		t.join()


def do_xiaoqu_chengjiao_spider(db_cj, region='浦东'):
	count = 0
	xq_list = db_cj.fetchall(region=region)
	for xq in xq_list:
		xiaoqu_chengjiao_spider(db_cj, xq[0])
		count += 1
		print '获取了%s小区的成交信息' % xq[0]
	print '获取了%s 区共 %s 个小区的成交记录' % (region, count)


def exception_write(fun_name, url):
	lock.acquire()
	f = open('log.txt', 'a')
	line = "%s %s\n" % (fun_name, url)
	f.write(line)
	f.close()
	lock.release()


def exception_read():
	lock.acquire()
	f = open('log.txt', 'r')
	lines = f.readlines()
	f = open('log.txt', 'w')
	f.truncate()
	f.close()
	lock.release()
	return lines


def exception_spider(db_cj):
	conut = 0
	excep_list = exception_read()
	while excep_list:
		for excep in excep_list:
			excep = excep.strip()
			if excep == "":
				continue
			excep_name, url = excep.split(" ", 1)
			if excep_name == "chengjiao_spider":
				chengjiao_spider(db_cj, url)
				conut += 1
			elif excep_name == "xiaoqu_chengjiao_spider":
				xiaoqu_chengjiao_spider(db_cj, url)
				conut += 1
			else:
				print "wrong format"
			print '处理了%d 异常url' % conut
		excep_list = exception_read()
	print 'all done'


if __name__ == "__main__":
	conn = mysql_wraper()
	# for region in regions:
	# 	do_xiaoqu_spider(conn, region)
	# for region in regionname:
	# 	do_xiaoqu_chengjiao_spider(conn, region)
	exception_spider(conn)

