#!/usr/bin/env python3

import sys
import requests
from requests.cookies import RequestsCookieJar
from lxml import etree

import time
import random

DOMAIN = 'http://dj.cs.ustc.edu.cn'

USERNAME = ''
PASSWORD = ''

def main():
	# Random delay
	print('Randomly delaying 1-300 seconds...')
	time.sleep(random.randint(1,3))

	# Check username and password
	global USERNAME, PASSWORD
	if not USERNAME:	USERNAME = input('请输入学号：')
	if not PASSWORD:	PASSWORD = input('请输入密码：')

	req = requests.Session()
	cookie_jar = RequestsCookieJar()
	login_payload = {
		'username':	USERNAME,
		'password':	PASSWORD
	}
	url = 'http://dj.cs.ustc.edu.cn/admin/index/login.html'

	# Open Login
	print('正在登录: %s' % url)
	r = req.post(url, data=login_payload, allow_redirects=False)
	cookie_jar.update(r.cookies)
	# print(cookie_jar.items())
	
	# Now set url to index.html
	url = 'http://dj.cs.ustc.edu.cn/admin/index/index.html'
	r = req.get(url, cookies=cookie_jar)

	# Now we have got the page. We should know what '待办事项' refers to
	dashboard_page = etree.HTML(r.text)
	iframe_link_path = dashboard_page.xpath("//*[@id='draggable']/div[2]/div[1]/dl[1]/dd[2]/a/@data-param")
	assert(len(iframe_link_path) == 1)
	iframe_link = DOMAIN + iframe_link_path[0]

	# Random delay before requesting daily report
	print('Randomly delaying 10-20 seconds...')
	time.sleep(random.randint(5,10))
	
	todo_events = []
	r = req.get(iframe_link, cookies=cookie_jar)
	assert(r.status_code == 200)
	events_page = etree.HTML(r.text)
	events = events_page.xpath("//div[@class='bDiv']/table/tbody/tr")
	for i in range(len(events)):
		event_name = events_page.xpath("//div[@class='bDiv']/table/tbody/tr[%d]/td[1]/text()" % (i+1))[0]
		event_status = events_page.xpath("//div[@class='bDiv']/table/tbody/tr[%d]/td[5]/text()" % (i+1))[0].strip()
		event_link = events_page.xpath("//div[@class='bDiv']/table/tbody/tr[%d]/td[6]/a/@href" % (i+1))[0]
		if event_status != '已办理':
			event_status = '\033[1;31m未办理\033[0m'
			todo_events.append((event_name, event_link))
		print('%s\t%s' % (event_name, event_status))

	print('=========================')
	for event in todo_events:
		sys.stdout.write('正在办理 %s' % event[0])
		event_full_link = DOMAIN + event[1]

		# Random delay before requesting daily report
		print('Randomly delaying 10-20 seconds...')
		time.sleep(random.randint(5,10))

		r = req.get(event_full_link, cookies=cookie_jar)
		commit_page = etree.HTML(r.text)
		commit_path = commit_page.xpath("//div[@class='bot']/a[1]/@href")[0]
		commit_url = DOMAIN + commit_path

		# Random delay before requesting daily report
		print('Randomly delaying 10-20 seconds...')
		time.sleep(random.randint(5,10))

		r = req.get(commit_url, cookies=cookie_jar)
		print(r.status_code == 200 and '成功' or '失败')

	return 0

if __name__ == '__main__':
	sys.exit(main())
