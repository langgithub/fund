# -*- coding: utf-8 -*-
import scrapy
import re
import time
import requests
from ..pipelines import *
from ..items import *
import threading
from scrapy_redis.spiders import RedisSpider


class ManagerSpider(RedisSpider):
    name = 'Manager'
    allowed_domains = ['www.howbuy.com']
    start_urls = ['http://www.howbuy.com/']
    mongo = MongoPipeline()
    redis = RedisPipeline()
    redis_key = "Manager"
    buzhou = 2

    def mongo_to_redis(self):
        while True:
            if self.redis.list_len(self.redis_key) == 0:
                seeds = self.mongo.manager_info_seed_find()
                print("查到基金经济人种子=======》" + str(seeds.count()) + "个")
                for seed in seeds:
                    self.redis.set_seed(self.redis_key, "https://www.howbuy.com/fund/manager/{0}/".format(seed["manager_code"]))
                print("redis 装入完毕，休息10s")
            time.sleep(10)

    def start_requests(self):
        if self.buzhou == 1:
            for url in self.start_urls:
                yield scrapy.Request(url=url, callback=self.parse_company)
                # t = threading.Thread(target=self.mongo_to_redis)
                # t.start()
        elif self.buzhou == 2:
            t = threading.Thread(target=self.mongo_to_redis)
            t.start()
        elif self.buzhou == 3:
            url = "https://www.howbuy.com/fund/manager/30062613/"
            yield scrapy.Request(url=url)
        elif self.buzhou == 4:
            url = "https://www.howbuy.com/fund/001558/"
            yield scrapy.Request(url=url)

    def parse(self, response):
        html = scrapy.Selector(text=response.body)
        item_manager=Manager2().getInstance()
        item_manager["manager_code"]=re.search("manager/(.*)/",response.url).group(1)
        if len(html.css("#dqszgs::attr(href)").extract())!=0:
            item_manager["current_company_code"] = re.search("company/(.*?)/",html.css("#dqszgs::attr(href)").extract()[0]).group(1)
            item_manager["current_company_name"] = html.css("#dqszgs::text").extract()[0]
        item_manager["person_instr"]=html.css("div.des_con::text").extract()[0].replace("\r\n","").replace(" ","").replace("\t","")
        content_m=html.css("div.content_m")
        for tr in content_m.css("tr"):
            tds=tr.css("td")
            for index in range(0,len(tds),2):
                if "首次任职时间" in str(tds[index].extract()):
                    item_manager["work_start"]=tds[index+1].css("::text").extract()[0]
                if "任基金经理时间" in str(tds[index].extract()):
                    item_manager["work_duration"]=tds[index+1].css("::text").extract()[0]
                if "历任公司数" in str(tds[index].extract()):
                    item_manager["work_company_num"]=tds[index+1].css("::text").extract()[0].replace("\r\n","").replace(" ","")
                if "跳槽频率" in str(tds[index].extract()):
                    item_manager["work_frequency"]=tds[index+1].css("::text").extract()[0]
                if "历史管理基金数" in str(tds[index].extract()):
                    item_manager["work_fund_num"]=tds[index+1].css("::text").extract()[0].replace("\r\n","").replace(" ","")
                if "从业年均回报" in str(tds[index].extract()):
                    item_manager["work_repay_avg"]=tds[index+1].css("::text").extract()[0]
        fund_info=";".join(html.css("div.content_des_con li::text").extract()).replace("\r\n","").replace(" ","")
        if len(html.css("div.top_right span.cRed::text").extract())!=0:
            item_manager["the_most_repay"]=html.css("div.top_right span.cRed::text").extract()[0]
        if len(html.css("div.top_right span.cGreen::text").extract()) != 0:
            item_manager["the_most_retreat"]=html.css("div.top_right span.cGreen::text").extract()[0]
        item_manager["ts"]=time.strftime("%Y-%m-%D %H:%M:%S", time.localtime(time.time()))
        item_manager["status"]=1

        #history
        trs=html.css("div#nTab4_0 tr")
        for index in range(1,len(trs)):
            manager_fund = ManagerFund().getInstance()
            tds=trs[index].css("td")
            manager_fund["manager_code"]=item_manager["manager_code"]
            manager_fund["fund_name"]=tds[0].css("a::text").extract()[0]
            manager_fund["fund_code"]=re.search("fund/(.*?)/",str(tds[0].css("a::attr(href)").extract())).group(1)
            manager_fund["company_name"]=item_manager["current_company_name"]
            manager_fund["company_code"] = item_manager["current_company_code"]
            manager_fund["fund_tpye"]=tds[1].css("::text").extract()[0]
            manager_fund["this_company_start"]=''
            manager_fund["this_company_duration"] = tds[3].css("::text").extract()[0]
            manager_fund["this_most_retreat"] = tds[4].css("::text").extract()[0]
            manager_fund["this_most_repay"] = tds[5].css("::text").extract()[0]
            manager_fund["ts"]=time.strftime("%Y-%m-%D %H:%M:%S", time.localtime(time.time()))
            manager_fund["status"]=1
            manager_fund["m_f_c"]=manager_fund["manager_code"]+"_"+manager_fund["fund_code"]+"_"+manager_fund["company_code"]
            #print(manager_fund)
            try:
                self.mongo.process_item(manager_fund)
            except Exception as e:
                print(e)

        trs=html.css("div.history_content tr.line_b")
        for tr in trs:
            tds=tr.css("td")
            company_name=tds[0].css("a::text").extract()[0]
            company_code=re.search("fund/company/(.*?)/",str(tds[0].css("a::attr(href)").extract())).group(1)
            current_trs=tds[1].css("table tr")
            for _tr in current_trs:
                _tds=_tr.css("td")
                manager_fund = ManagerFund().getInstance()
                manager_fund["manager_code"] = item_manager["manager_code"]
                manager_fund["company_name"] = company_name
                manager_fund["company_code"] = company_code
                manager_fund["fund_name"] = _tds[0].css("a::text").extract()[0]
                manager_fund["fund_code"] = re.search("fund/(.*?)/",str(_tds[0].css("a::attr(href)").extract())).group(1)
                manager_fund["fund_tpye"]=_tds[1].css("::text").extract()[0]
                manager_fund["this_company_start"]=_tds[2].css("::text").extract()[0]
                manager_fund["this_company_duration"] = _tds[3].css("::text").extract()[0]
                manager_fund["this_most_retreat"] = ''
                manager_fund["this_most_repay"] = _tds[4].css("::text").extract()[0]
                manager_fund["ts"] = time.strftime("%Y-%m-%D %H:%M:%S", time.localtime(time.time()))
                manager_fund["status"] = 1
                manager_fund["m_f_c"] = manager_fund["manager_code"] + "_" + manager_fund["fund_code"] + "_" + \
                                        manager_fund["company_code"]

                #print(manager_fund)
                try:
                    self.mongo.process_item(manager_fund)
                except Exception as e:
                    print(e)

        #更细种子状态
        self.mongo.manager_info_update(item_manager)




