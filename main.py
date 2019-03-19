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

list_url    = "https://www.douban.com/group/kuakua/discussion?type=essence&start=0";
content_url = "";

save_path = 'save/';

headers = {
	"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
};

myRequests = requests.Session();
myRequests.headers.update(headers);

address_list = [];
content_list = [];
stat_info    = {};

def main():

	# 读取配置
	config = readJson('config.json');

	headers['Cookie'] = config['cookie'];

	# catt todo 循环获取列表

	# # 获取列表页面
	# # html = getHtml(list_url);
	# # saveFile(html, save_path + 'list.html');
	# html = readFile(save_path + 'list.html');

	# # 解析
	# list_ = handleListHtml(html);

	# # 推入全局数组
	# for item in list_:
	# 	address_list.append(item);

	# # 保存到文件
	# saveJson(address_list, save_path + 'address_list.json');


	# 从文件加载
	address_list = readJson(save_path + 'address_list.json');


	address = address_list[0];

	url = address['href'];

	# content = getHtml(url);
	# saveFile(content, save_path + 'content.html');

	content = readFile(save_path + 'content.html');

	item = handleContentHtml(content);

	item['info']         = address;

	content_list.append(item);

	saveJson(content_list, save_path + 'content_list.json');

	# for address in address_list:
		
	# 	item_ = {};

	# 	item_['title']   = address['title'];
	# 	item_['address'] = address['href'];
	# 	item_['content'] = '';

	# print(address_list);



	# print("Hello world");


def getHtml(url):

	html = '';

	r = requests.get(url = url, headers = headers);

	html = r.content;

	return html;

def del_content_blank(s):
	clean_str = re.sub(r'\n|&nbsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020', '', s) 
	return clean_str 

def handleListHtml(html):

	bs = BeautifulSoup(html, 'html.parser');

	table = bs.find('table', class_='olt');

	title_list = table.find_all('a', href = re.compile(r'.*?/topic/.*'));

	list_ = [];


	for title in title_list:
		item = {};

		item['title'] = title['title'];
		item['href']  = title['href'];

		list_.append(item);

	return list_;

def handleContentHtml(html):

	data = {};

	data['content']      = '';
	data['popular_list'] = [];
	data['comment_list'] = [];

	bs = BeautifulSoup(html, 'html.parser');

	article = bs.find('div', class_ = 'article');

	# 获取内容
	topic_content = article.find('div', class_ = 'topic-richtext');

	t_ = del_content_blank(topic_content.text);

	# print(t_);

	data['content'] = t_;

	popular_list = article.find('ul', class_ = 'topic-reply popular-bd');
	popular_list = popular_list.find_all('div', class_ = 'reply-doc content');

	# 获取高赞列表
	for popular in popular_list:

		t_ = del_content_blank(popular.find('p').text);

		# print(t_);

		data['popular_list'].append(t_);

	
	comment_list = article.find('ul', id = 'comments').find_all('li');

	# 获取评论列表
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