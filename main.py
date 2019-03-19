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

list_url       = "https://www.douban.com/group/kuakua/discussion?type=essence&start=0";
save_path = 'save/';

headers = {
	"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
};

myRequests = requests.Session();
myRequests.headers.update(headers);

address_list = [];


def main():

	# 读取配置
	config = readJson('config.json');

	headers['Cookie'] = config['cookie'];

	# 获取列表页面
	html = readFile(save_path + 'list.html');

	# 解析
	list_ = handleListHtml(html);

	# 推入全局数组
	for item in list_:
		address_list.append(item);


	# 保存到文件
	saveJson(address_list, save_path + 'address_list.json');

	# html = getHtml(list_url);

	# saveFile(html, save_path + 'list.html');

	# print("Hello world");


def getHtml(url):

	html = '';

	r = requests.get(url = url, headers = headers);

	html = r.content;

	return html;

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

	text = json.dumps(data);

	text = text.decode('unicode_escape').encode('utf-8');

	saveFile(text, path);


def readJson(path):

	text = readFile(path);

	dict_ = json.loads(text)

	return dict_;

main();