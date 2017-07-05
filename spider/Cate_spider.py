#encoding:utf-8

import scrapy
from Start_Urls import Start_Urls
import re
from scrapy.spiders import BaseSpider
from baidu_crawl.items import ZhidaoItem

class CateSpider(BaseSpider):
	name = "cate"
	allowed_domains = ["baidu.com"]

	start_urls = [
	"https://zhidao.baidu.com/search?word="
	]

	def __init__(self, relation=None, *args, **kwargs):
		super(CateSpider, self).__init__(*args, **kwargs)
		#self.start_urls = ['https://zhidao.baidu.com/search?word=%s' % (relation)]
		Urls = Start_Urls()
		self.start_urls = Urls.getStartUrls()


	def parse(self, response):
		for sel in response.xpath('//title/text()'):
			title = sel.extract()
			entity = title.strip().split(' ')[0]
			entity = entity.replace("百度知道搜索_", "")
			relation = title.strip().split(' ')[1]
			if entity != None and relation != None:
				break
			else:
				print "Can't find title"


		for sel in response.xpath('//a[@class="ti"]'):
			name = sel.re(r'href=\"(.*?)\"')
			if not name:
				print 'Can\'t find sel'
			else:
				url_new = name[0].replace("http", "https").split("?")
				request = scrapy.Request(url_new[0], self.parse_page)
				request.meta['link'] = url_new[0]
				request.meta['entity'] = entity
				request.meta['relation'] = relation
				yield request



	def parse_page(self, response):
		#if response.status == 666:
		#	request = scrapy.Request(response.meta['link'], self.parse_page, cookies = response.headers.getlist('Set-Cookie'))
		#	return request

		que_str = ""
		content_str = ""
		quality_str = ""
		like_str = "0"

		ques = re.findall(r'<span class=\"ask-title[ ]*\">(.*?)</span>', response.body)
		if ques:
			que_str = ques[0].decode('gbk').encode('utf-8')
		ans = re.findall(r'<pre id="best-content.*?>(.*?)</pre>', response.body)
		#if ans:
		#	ans_str = ans[0].replace("<br />", " ")
		#	ans_str = re.sub(r'<.*?>', "", ans[0].decode('gbk').encode('utf-8'))
		quality = re.findall(r'<span class="mr-15\">(.*?)</span>', response.body)
		if quality:
			quality_str = quality[0].decode('gbk').encode('utf-8').replace("采纳率：", "")

		like = re.findall(r'data-evaluate="(.*?)"', response.body)
		if like:
			like_str = like[0].decode('gbk').encode('utf-8')

		content = re.findall(r'<meta name="description" content="(.*?)"/>', response.body)
		if content:
			content_str = content[0].decode('gbk').encode('utf-8').replace(que_str, "")

		similar_question = []
		for sel in response.xpath('//a[@class="related-link"]/text()'):
			#name = sel.xpath('string(.)').extract()[0].decode('gbk').encode('utf-8')
			name = sel.extract().encode('utf-8')
			if name != "\n":
				similar_question.append(name)




			
		item = ZhidaoItem()
		item['question'] = que_str
		item['link'] = response.meta['link']
		item['entity'] = response.meta['entity']
		item['relation'] = response.meta['relation']
		item['ans_quality'] = quality_str
		item['like'] = like_str
		item['similar_question'] = similar_question

		if content:
			item['content'] = content_str
		else:
			item['content'] = "can't find"

		#if "picenc" in response.body:
		#	item['code'] = "No"
		#if content_str != None and (content_str in ans_str) == False:
		#	item['code'] = "No"
			

		return item