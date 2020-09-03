#!usr/bin/env python
# _*_ coding:utf-8 _*_
import requests
import json
import smtplib
from email.mime.text import MIMEText
from multiprocessing.dummy import Pool as ThreadPool
import time
#其中data可以使用Fiddler从手机APP中抓取
careinfo=[{
	'flightNo':['HO1019'],
	'flightNoCheck':{},
	'data':{"directType":"D","sendCode":"SHA","channelCode":"MOBILE","platformInfo":"ios","sign":"67fbe5b2f3c598fff20821d3f33de1a3","flightType":"OW","loginKeyInfo":"6D46310A6EFC2615C8512C4CEC9DA3DB","returnDate":"2020-11-16","departureDate":"2020-09-11","clientVersion":"6.1.0","ffpId":"9568456","arrCode":"KMG","blackBox":"eyJ0b2tlbklkIjoiMG5GSk9yZk9wTkxaa1A0UHkyS2lzcFRcL0dUTk80VW4rd3N2dStVNlwvMEd4K2ltdXlGYndMU3BUSnhoejJqZjlcL3JkdGRMSGc0eEh4bGVIWis2MTNCMlE9PSIsIm9zIjoiaU9TIiwic2VxSWQiOiIxNTk5MDQ1MDIwMTMzNzE4NDc3IiwicHJvZmlsZVRpbWUiOjE1NzUsInZlcnNpb24iOiIzLjYuMiJ9","tripType":"D","ffpCardNo":"6928138162"}
},{
	'flightNo':['HO1095'],
	'flightNoCheck':{},
	'data':{"departureDate":"2020-09-12","blackBox":"eyJ0b2tlbklkIjoiMG5GSk9yZk9wTkxaa1A0UHkyS2lzcFRcL0dUTk80VW4rd3N2dStVNlwvMEd4K2ltdXlGYndMU3BUSnhoejJqZjlcL3JkdGRMSGc0eEh4bGVIWis2MTNCMlE9PSIsIm9zIjoiaU9TIiwic2VxSWQiOiIxNTk5MDQ1MDIwMTMzNzE4NDc3IiwicHJvZmlsZVRpbWUiOjE1NzUsInZlcnNpb24iOiIzLjYuMiJ9","clientVersion":"6.1.0","flightType":"OW","sign":"7130af5dd33c0f63c78ccf74f0b9abe5","ffpCardNo":"6928138162","loginKeyInfo":"6D46310A6EFC2615C8512C4CEC9DA3DB","arrCode":"KMG","sendCode":"SHA","platformInfo":"ios","tripType":"D","channelCode":"MOBILE","returnDate":"2020-11-16","ffpId":"9568456","directType":"D"}
},{
	'flightNo':['HO1227'],
	'flightNoCheck':{},
	'data':{"clientVersion":"6.1.0","tripType":"D","ffpCardNo":"6928138162","platformInfo":"ios","directType":"D","arrCode":"LJG","sendCode":"SHA","flightType":"OW","blackBox":"eyJ0b2tlbklkIjoiTnFReVwvczh1cXAxMmF0N0I2Uk9uSWNaSEhlNUhEVG1NQzM2aElXMlZFTVFlNkhTZ1JhZ2pMZklNelhuWDJEekhFKzhwXC9HNFwvXC9pckIzVXlPayt0aFZnPT0iLCJvcyI6ImlPUyIsInNlcUlkIjoiMTU5OTA1MDk3MzAwNjM4MjU1OSIsInByb2ZpbGVUaW1lIjozMTgsInZlcnNpb24iOiIzLjYuMiJ9","sign":"66b2d1ece1141329498deaa9f27508b7","loginKeyInfo":"6D46310A6EFC2615C8512C4CEC9DA3DB","departureDate":"2020-09-18","returnDate":"2020-11-16","channelCode":"MOBILE","ffpId":"9568456"}
}]
url = 'http://homobile.juneyaoair.com:86/v2/flight/AvFare'
headers = {
    'Host':'homobile.juneyaoair.com:86',
    'platformInfo':'ios',
    'Accept':'*/*',
    'Connection':'keep-alive',
    'Accept-Language':'zh-cn',
    'clientVersion':'6.1.0',
    'token':'www.juneyaoair.com',
    'channelCode':'MOBILE',
    'versionCode':'61000',
    'Accept-Encoding':'gzip, deflate',
    'User-Agent':'JuneYaoAir/61000 CFNetwork/1128.0.1 Darwin/19.6.0',
    'Connection':'keep-alive',
    'Content-Type':'application/json'
}
def sendemail(content):
	# 发送者邮箱地址
	senderMail = 'xxxxx@qq.com'
	# 发送者 QQ邮箱授权码
	authCode = 'xxxxxx'
	# 接收者邮箱地址
	receiverMail = 'xxxxxx@qq.com'
	# 邮件主题
	subject = '吉祥航空余票监控'
	# 邮件内容
	content = content
	msg = MIMEText(content, 'plain', 'utf-8')
	msg['Subject'] = subject
	msg['From'] = senderMail
	msg['To'] = receiverMail
	try:
		server = smtplib.SMTP_SSL('smtp.qq.com', smtplib.SMTP_SSL_PORT)
		print('成功连接到邮件服务器')
		server.login(senderMail, authCode)
		print('成功登录邮箱')
		server.sendmail(senderMail, receiverMail, msg.as_string())
		print('邮件发送成功')
	except smtplib.SMTPException as e:
		print('邮件发送异常')
	finally:
		server.quit()
def get_date(careinfo):
	s = json.dumps(careinfo['data'])
	try:
		r = requests.post(url=url, headers=headers, data=s,timeout=30)
		jsons = json.loads(r.text)
		flightInfoList = jsons['flightInfoList']
		# print(jsons)
		for flightInfo in flightInfoList:
			#     print(flightInfo)
			if (flightInfo['flightNo'] in careinfo['flightNo']) or len(careinfo['flightNo']) == 0:
				#         print(flightInfo)
				for cabinFare in flightInfo['cabinFareList']:
					#             print(cabinFare)
					if cabinFare['cabinCode'] == 'X':
						# print(u'您所监控的航班:%s (%s%s-%s%s)' % (
						# flightInfo['flightNo'], flightInfo['depCityName'], flightInfo['depAirportName'],
						# flightInfo['arrCityName'], flightInfo['arrAirportName']))
						# print(u'起飞时间:' + flightInfo['depDateTime'])
						# print(u'到达时间:' + flightInfo['arrDateTime'])
						str = u'您所监控的航班:%s (%s%s-%s%s)\n起飞时间:%s\n到达时间:%s\n' % (
							flightInfo['flightNo'], flightInfo['depCityName'], flightInfo['depAirportName'],
							flightInfo['arrCityName'], flightInfo['arrAirportName'], flightInfo['depDateTime'],
							flightInfo['arrDateTime'])
						flightNoStatus = careinfo['flightNoCheck'].get(flightInfo['flightNo'], "")
						if cabinFare['cabinNumber'] == 'A':
							str = str + u'畅飞卡可兑换客舱出现了！'
							if not (flightNoStatus) or flightNoStatus == '0':
								flightNoStatus = 'A'
								sendemail(str)
						elif cabinFare['cabinNumber'] == '0':
							str = str + u'畅飞卡可兑换客舱已兑完！'
							if not (flightNoStatus) or flightNoStatus != '0':
								flightNoStatus = '0'
								print('0')
						elif int(cabinFare['cabinNumber']) > 0:
							str = str + u'畅飞卡可兑换客舱还剩' + cabinFare['cabinNumber'] + u'张！'
							if not (flightNoStatus) or flightNoStatus == '0':
								flightNoStatus = cabinFare['cabinNumber']
								sendemail(str)
						careinfo['flightNoCheck'][flightInfo['flightNo']] = flightNoStatus
						print(str)
						print('---------------------')
						print(careinfo['flightNoCheck'])
	except Exception as e:
		print(e)
if __name__ == '__main__':
	pool = ThreadPool(1)  # 降速
	try:
		for m in range(0, 6000):
			print(m)
			results = pool.map(get_date, careinfo)
			time.sleep(60)
	except Exception as e:
		print(e)
	pool.close()
	pool.join()