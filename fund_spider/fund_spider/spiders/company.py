# -*- coding: utf-8 -*-
import scrapy
import re
import time
import requests
from ..pipelines import *
from ..items import *
import threading
from scrapy_redis.spiders import RedisSpider


class CompanySpider(RedisSpider):
    name = 'company'
    allowed_domains = ['www.howbuy.com']
    start_urls = ['https://www.howbuy.com/fund/company/']
    mongo = MongoPipeline()
    redis = RedisPipeline()
    redis_key = "fund"
    buzhou = 2

    def mongo_to_redis(self):
        while True:
            if self.redis.list_len(self.redis_key) == 0:
                seeds = self.mongo.fund_seed_find()
                print("查到基金列表种子=======》" + str(seeds.count()) + "个")
                for seed in seeds:
                    self.redis.set_seed(self.redis_key, seed["url"])
                # seeds = self.mongo.manager_seed_find()
                # print("查到经纪人列表种子=======》" + str(seeds.count()) + "个")
                # for seed in seeds:
                #     print(seed)
                #     self.redis.set_seed(self.redis_key, "https://www.howbuy.com/fund/manager/" + seed["code"] + "/")
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
            url = "https://www.howbuy.com/fund/company/80041198/"
            yield scrapy.Request(url=url)
        elif self.buzhou == 4:
            url = "https://www.howbuy.com/fund/001558/"
            yield scrapy.Request(url=url)

    def parse_company(self, response):
        html = scrapy.Selector(text=response.body)
        item = Company()
        tds = html.css("#company-chart > tbody td")
        for index in range(1, len(tds), 10):
            company_name = tds[index].css("::text").extract()[0]
            company_url = "https://www.howbuy.com" + tds[index].css("::attr(href)").extract()[0]
            item["name"] = company_name
            item["url"] = company_url
            item["code"] = re.search("/fund/company/(.*)/", company_url).group(1)
            item["ts"] = time.strftime("%Y-%m-%D %H:%M:%S", time.localtime(time.time()))
            item["status"] = 0
            self.requset_fundlist(company_url + "fundlist/")
            self.requset_manager(url=company_url + "managerlist/")
            try:
                self.mongo.process_item(item)
            except Exception as e:
                if "duplicate" in str(e):
                    log.msg(e,level=log.WARNING)
                    return
    def requset_manager(self, url):
        response = requests.get(url=url)
        html = scrapy.Selector(text=response.content)
        bodys = html.css("div.content_left div.manager_list div.nTab30 table")
        if len(bodys) != 0:
            trs = bodys[0].css("tr")
            for index in range(1, len(trs)):
                item = Manager().getInstance()
                item["word_status"] = "在职"
                item["name"] = ",".join(trs[index].css("td:nth-child(2) a::text").extract())
                item["code"] = re.search("manager/(.*?)/", str(trs[index].extract())).group(1)
                item["cur_company_code"] = re.search("company/(.*?)/managerlist", response.url).group(1)
                item["cur_company_start"] = ",".join(trs[index].css("td:nth-child(3) span::text").extract())
                item["cur_company_dur"] = ",".join(trs[index].css("td:nth-child(4) span::text").extract())
                item["total_dur"] = ",".join(trs[index].css("td:nth-child(5) span::text").extract())
                item["cur_company_funds"] = ",".join(trs[index].css("td:nth-child(6) span::text").extract())
                item["ts"] = time.strftime("%Y-%m-%D %H:%M:%S", time.localtime(time.time()))
                item["status"] = 0
                self.mongo.process_item(item)
        if len(bodys)==2:
            trs = bodys[1].css("tr")
            for index in range(1, len(trs)):
                item = Manager().getInstance()
                item["word_status"] = "离职"
                item["code"] = re.search("manager/(.*?)/", str(trs[index].extract())).group(1)
                item["name"] = trs[index].css("td:nth-child(2) a::text").extract()[0]
                item["cur_company_code"] = re.search("company/(.*?)/managerlist", response.url).group(1)
                item["cur_company_start"] = ",".join(trs[index].css("td:nth-child(3) span::text").extract())
                item["cur_company_end"] = ",".join(trs[index].css("td:nth-child(4) span::text").extract())
                item["cur_company_dur"] = ",".join(trs[index].css("td:nth-child(5) span::text").extract())
                item["total_dur"] = ",".join(trs[index].css("td:nth-child(6) span::text").extract())
                new_company = trs[index].css("td:nth-child(7) a")
                if len(new_company) != 0:
                    item["new_company"] = new_company.css("::text").extract()[0]
                item["ts"] = time.strftime("%Y-%m-%D %H:%M:%S", time.localtime(time.time()))
                item["status"] = 0
                self.mongo.process_item(item)

    def requset_fundlist(self, url):
        response = requests.get(url=url)
        html = scrapy.Selector(text=response.content)
        item_fund = Fund()
        tbodys = html.css("div.fund_list tbody")
        for tbody in tbodys:
            trs = tbody.css("tr")
            for tr in trs:
                td = tr.css("td:nth-child(3)")
                item_fund["cur_company_code"] = re.search("company/(.*?)/fundlist", response.url).group(1)
                item_fund["name"] = td.css("a::text").extract()[0]
                item_fund["url"] = "https://www.howbuy.com" + td.css("a::attr(href)").extract()[0]
                item_fund["code"] = re.search("/fund/(.*)/", item_fund["url"]).group(1)
                item_fund["ts"] = time.strftime("%Y-%m-%D %H:%M:%S", time.localtime(time.time()))
                item_fund["status"] = 0
                self.mongo.process_item(item_fund)

    def parse(self, response):
        html=scrapy.Selector(text=response.body)
        item = Fund().getInstance()
        code = re.search("fund/(.*)/", response.url).group(1)
        item["url"]=response.url
        if "fund" in response.url:
            content=self.request_data(code)

            # 持仓数据（股票组合）
            if re.search("gpzhListData = ({[\s\S]*?});", content) is not None:
                item["gpzhListData"] = re.search("gpzhListData = ({[\s\S]*?});", content).group(1).replace("\r\n","")
            # 行业饼状图
            if re.search("hyPieData = ({[\s\S]*?});", content) is not None:
                item["hyPieData"] = re.search("hyPieData = ({[\s\S]*?});", content).group(1).replace("\r\n","")
            # 资产配置饼图
            if re.search("zcPieData = ({[\s\S]*?});", content) is not None:
                item["zcPieData"] = re.search("zcPieData = ({[\s\S]*?});", content).group(1).replace("\r\n","")
            # 排名走势数据（基金涨幅）
            item["jjpmChartData"] = re.search("jjpmChartData = ({[\s\S]*?});", content).group(1).replace("\r\n","")


            # 历史走势
            item["navList"] = re.search("navList:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListTenDay"] = re.search("navStrListTenDay:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListOneMonth"] = re.search("navStrListOneMonth:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListThreeMonth"] = re.search("navStrListThreeMonth:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListSixMonth"] = re.search("navStrListSixMonth:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListOneYear"] = re.search("navStrListOneYear:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListTwoYears"] = re.search("navStrListTwoYears:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListThreeYears"] = re.search("navStrListThreeYears:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListFiveYears"] = re.search("navStrListFiveYears:([[\s\S]*?]),", content).group(1).replace("\r\n","")
            item["navStrListJnylDay"] = re.search("navStrListJnylDay:([[\s\S]*?]),", content).group(1).replace("\r\n","")

            # 历史基金人
            item["jlbdStrList"] = re.search("jlbdStrList:([[\s\S]*?])", content).group(1).replace("\r\n","").replace(" ","")
            #item["html"]+=content

        #基金经理
        hrefs=html.css("#nTab2_0 > div.file_Manager div.manager_box ul.item_4 li:nth-child(1) a::attr(href)")
        manager_code=""
        for href in hrefs:
            manager_code+=re.search("manager/(.*?)/",href.extract()).group(1)+","
        item["manager_code"]=manager_code[:-1]

        #基金公司
                       # nTab2_0 > div.file_Co  ul > li:nth-child(1)
        a_com=html.css("#nTab2_0 > div.file_Co  ul > li:nth-child(1) > a::attr(href)")
        item["company_code"]=re.search("company/(.*?)/",a_com.extract()[0]).group(1)

        #基金概况
        stream=self.request_jjgk(code)
        j_html=scrapy.Selector(text=stream)
        trs=j_html.css("table tr")
        for tr in trs:
            tds=tr.css("td")
            for index in range(0,len(tds),2):
                if "基金简称" in tds[index].extract():
                    item["jjjc"]=",".join(tds[index+1].css("::text").extract())
                if "基金代码 " in tds[index].extract():
                    item["jjdm"]=",".join(tds[index+1].css("::text").extract())
                if "基金全称" in tds[index].extract():
                    item["jjqc"]=",".join(tds[index+1].css("::text").extract())
                if "基金类型" in tds[index].extract():
                    item["jjlx"]=",".join(tds[index+1].css("::text").extract())
                if "成立日期" in tds[index].extract():
                    item["clrq"]=",".join(tds[index+1].css("::text").extract())
                if "基金状态" in tds[index].extract():
                    item["jjzt"]=",".join(tds[index+1].css("::text").extract())
                if "交易状态" in tds[index].extract():
                    item["jyzt"]=",".join(tds[index+1].css("::text").extract())
                if "基金公司" in tds[index].extract():
                    item["jjgs"]=",".join(tds[index+1].css("::text").extract())
                if "基金经理" in tds[index].extract():
                    item["jjjl"]="".join(tds[index+1].css("::text").extract()).replace("\r\n","").replace(" ","").replace("\t","")
                if "基金管理费" in tds[index].extract():
                    item["jjglf"]=",".join(tds[index+1].css("::text").extract())
                if "基金托管费" in tds[index].extract():
                    item["jjtgf"]=",".join(tds[index+1].css("::text").extract())
                if "首募规模" in tds[index].extract():
                    item["smgm"]=",".join(tds[index+1].css("::text").extract())
                if "最新份额" in tds[index].extract():
                    item["zxfe"]=",".join(tds[index+1].css("::text").extract())
                if "托管银行" in tds[index].extract():
                    item["tgyh"]=",".join(tds[index+1].css("::text").extract())
                if "最新规模" in tds[index].extract():
                    item["zxgm"]= ",".join(tds[index+1].css("::text").extract())
        print(item)
        item["ts"] = time.strftime("%Y-%m-%D %H:%M:%S", time.localtime(time.time()))
        item["status"] = 1
        self.mongo.fund_info_update(item)


    def request_data(self, code):
        url = "https://static.howbuy.com/??/upload/auto/script/fund/jzzs_{0}.js,/upload/auto/script/fund/jjjl_{1}.js,/upload/auto/script/fund/data_{2}.js"
        response=requests.get(url.format(code,code,code))
        return response.text

    def request_jjgk(self,code):
        url="https://www.howbuy.com/fund/ajax/gmfund/fundsummary.htm?jjdm={0}".format(code)
        response=requests.get(url)
        return response.content



