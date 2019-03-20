#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function

import os
import requests
import re
import time
import xml.dom.minidom
import json
import sys
import math
import subprocess
import ssl
import threading
from bs4 import BeautifulSoup

list_url    = "https://www.douban.com/group/kuakua/discussion?type=essence&start=";
content_url = "";

save_path = 'save/';

save_address_list = save_path + 'address_list.json';
save_content_list = save_path + 'content_list.json';
save_stat_info    = save_path + 'stat_info.json';

headers = {
	"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
};

myRequests = requests.Session();
myRequests.headers.update(headers);

start_page = 1;
target_page  = 30;

address_list = [];
content_list = [];
stat_info    = {
	'content_count': 0,
	'popular_count': 0,
	'comment_count': 0,
};

def main():

	# 读取配置
	config = readJson('config.json');

	headers['Cookie'] = config['cookie'];

	func_list();
	func_content();

	saveJson(stat_info, save_stat_info);
	print("\n\n所有内容抓取完毕。 \n\n主题: %s 条; 高赞回复: %s 条; 回复: %s 条" % ( stat_info['content_count'], stat_info['popular_count'], stat_info['comment_count'] ));

def func_content():

	address_list               = readJson(save_address_list);
	content_count              = len(address_list);
	stat_info['content_count'] = content_count;
	i                          = 0;

	for address in address_list:
		i = i + 1;

		url = address['href'];
		# url = 'https://www.douban.com/group/topic/134589834/';

		# 延时 0.1 秒

		if(i % 60 == 0):
			time.sleep(1);
		elif(i % 15 == 0):
			time.sleep(0.1);
		else:
			# time.sleep(0.01);
			pass

		print('\n正在抓取... (%s/%s) \n标题: %s \n地址: %s' % (i, content_count, address['title'].encode('utf-8'), address['href'].encode('utf-8')));


		# content = readFile(save_path + 'content.html');
		content = getHtml(url);

		print('正在解析...');

		item = handleContentHtml(content);

		item['info'] = address;

		content_list.append(item);

		popular_count = len(item['popular_list']);
		comment_count = len(item['comment_list']);

		stat_info['popular_count'] += popular_count;
		stat_info['comment_count'] += comment_count;

		print('完成, 高赞 %s 条, 评论 %s 条' % (popular_count, comment_count));

		# 保存
		saveJson(content_list, save_content_list);

	print('\n内容抓取完成, 已经保存至: ' + save_content_list);



def func_list():

	# 获取列表页面
	
	for page in xrange(start_page, target_page + 1):

		url = list_url + str(25 * (page - 1));

		print("正在获取列表第 %s/%s 页, 地址: %s" % (page, target_page, url));

		# 延时 0.1 s
		time.sleep(0.1);

		html = getHtml(url);
		# saveFile(html, save_path + 'list.html');
		# html = readFile(save_path + 'list.html');

		# 解析
		list_ = handleListHtml(html);

		# 推入全局数组
		for item in list_:
			address_list.append(item);

		count = len(list_);

		print("第 %s/%s 页获取完成, 共 %s 条" % (page, target_page, count));

		# 保存到文件
		saveJson(address_list, save_address_list);

	total_count = len(address_list);
	stat_info['content_count'] = total_count;


	print("列表页面采集完成, 共计 %s 页, %s 条, 已经存储到 %s" % (page - start_page + 1, total_count, save_address_list));




def getHtml(url):

	html = '';

	r = requests.get(url = url, headers = headers);

	html = r.content;

	return html;

def del_content_blank(s):
	clean_str = re.sub(r'\n|\r|&nbsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020', '', s);

	# 转义反斜杠和双引号
	clean_str = re.sub(r'\\', '\\\\', s);
	clean_str = re.sub(r'\"', '\\\"', s);

	return clean_str 

def handleListHtml(html):

	bs = BeautifulSoup(html, 'html.parser');

	table = bs.find('table', class_='olt');

	title_list = table.find_all('a', href = re.compile(r'.*?/topic/.*'));

	list_ = [];


	for title in title_list:
		item = {};

		item['title'] = del_content_blank(title['title']);
		item['href']  = title['href'];

		list_.append(item);

	return list_;

def handleContentHtml(html):

	data = {};

	data['popular_list'] = [];
	data['comment_list'] = [];

	bs = BeautifulSoup(html, 'html.parser');

	article = bs.find('div', class_ = 'article');

	popular_list = article.find('ul', class_ = 'topic-reply popular-bd');

	if(popular_list != None):
		popular_list = popular_list.find_all('div', class_ = 'reply-doc content');

		# 获取高赞列表
		for popular in popular_list:

			t_ = del_content_blank(popular.find('p').text);

			# print(t_);

			data['popular_list'].append(t_);

	
	comment_list = article.find('ul', id = 'comments').find_all('li');

	for comment in comment_list:

		quote = comment.find('div', class_ = 'reply-quote');

		if(quote != None):
			continue;

		t_ = del_content_blank(comment.find('p').text);
		# print(t_);

		data['comment_list'].append(t_);

	return data;


def saveFile(text, path): 

	try:

		f = open(path, 'w');
		f.write(text);

	finally:

		f.close();

def readFile(path): 

	text = None;

	try:
		f = open(path, 'r');
		text = f.read();

	finally:

		f.close();

	return text;

def saveJson(data, path):

	text = json.dumps(data, indent = 4);

	text = text.decode('unicode_escape').encode('utf-8');

	saveFile(text, path);


def readJson(path):

	text = readFile(path);

	dict_ = json.loads(text)

	return dict_;

main();