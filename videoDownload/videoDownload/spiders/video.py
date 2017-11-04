# -*- coding: utf-8 -*-
import scrapy
import logging
import json
from scrapy import Request
import requests
class VideoSpider(scrapy.Spider):
    name = "video"
    allowed_domains = ["support.shimadzu.com.cn"]
    start_urls = ['https://support.shimadzu.com.cn/']
    startUrl="https://support.shimadzu.com.cn/an/training/online-learning.html#91"
    headers={
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch, br',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'no-cache',
        'Connection':'keep-alive',
        'Cookie':'acw_tc=AQAAAFpyVGPTVAAA8kVJ3/hkwxQku47W',
        'Host':'support.shimadzu.com.cn',
        'Pragma':'no-cache',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    tidList=[]
    def start_requests(self):
        yield Request(url=self.startUrl,callback=self.parse,headers=self.headers,dont_filter=True)
    def parse(self, response):
        #logging.info(response.xpath("/html/body/div[2]/div/div[1]/div/div[1]/div[2]/div[1]/div[1]/@tid").extract_first())
        dataLength=len(response.xpath("/html/body/div[2]/div/div[1]/div/div[1]/div[2]/div[1]/div"))+1
        logging.info(dataLength)
        for i in range(dataLength):
            num="/html/body/div[2]/div/div[1]/div/div[1]/div[2]/div[1]/div["+str(i)+"]/@tid"
            tid=response.xpath(num).extract_first()
            if tid:
                self.tidList.append(tid)
        for item in self.tidList:
            yield scrapy.FormRequest(url ="https://support.shimadzu.com.cn/an/json/resource.json",formdata = {"tid":str(item)},callback = self.parse_page)
    def parse_page(self,response):
        data=json.loads(response.text)
        for j in range(len(data)):
            for item in data[j]:
                if j==1:
                    for obj in item["data"]:
                        if obj["vedioCode"]:
                            self.downloadVideo(obj)
                else:
                    if item["vedioCode"]:
                        self.downloadVideo(item)
    def downloadVideo(self,item):
        url="https://plvod01.videocc.net/1f41d2259c/"+item["vedioCode"][-3:-2]+'/'+item["vedioCode"]+".flv?"
        r=requests.get(url,stream=True)
        with open("E:\\video\\"+item["title"]+".flv","wb") as f:
            f.write(r.content)
