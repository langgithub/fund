# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Company(scrapy.Item):
    code=scrapy.Field()
    name=scrapy.Field()
    url=scrapy.Field()
    ts=scrapy.Field()
    status=scrapy.Field()

class Fund(scrapy.Item):
    code=scrapy.Field()
    name=scrapy.Field()
    url=scrapy.Field()
    ts=scrapy.Field()
    cur_company_code=scrapy.Field()
    status=scrapy.Field()
    gpzhListData=scrapy.Field()
    hyPieData = scrapy.Field()
    zcPieData = scrapy.Field()
    jjpmChartData = scrapy.Field()
    navList = scrapy.Field()
    navStrListTenDay = scrapy.Field()
    navStrListOneMonth = scrapy.Field()
    navStrListThreeMonth = scrapy.Field()
    navStrListSixMonth = scrapy.Field()
    navStrListOneYear=scrapy.Field()
    navStrListTwoYears = scrapy.Field()
    navStrListThreeYears = scrapy.Field()
    navStrListFiveYears = scrapy.Field()
    navStrListJnylDay = scrapy.Field()
    jlbdStrList = scrapy.Field()
    manager_code=scrapy.Field()
    company_code = scrapy.Field()
    jjjc=scrapy.Field()
    jjdm=scrapy.Field()
    jjqc = scrapy.Field()
    jjlx = scrapy.Field()
    clrq = scrapy.Field()
    jjzt = scrapy.Field()
    jyzt = scrapy.Field()
    jjgs = scrapy.Field()
    jjjl = scrapy.Field()
    jjglf = scrapy.Field()
    jjtgf=scrapy.Field()
    smgm = scrapy.Field()
    zxfe = scrapy.Field()
    tgyh = scrapy.Field()
    zxgm = scrapy.Field()
    html= scrapy.Field()
    def getInstance(self):
        self["code"],self["name"],self["url"],self["ts"]='','','',''
        self["cur_company_code"], self["status"], self["gpzhListData"], self["hyPieData"] = '', '', '', ''
        self["zcPieData"], self["jjpmChartData"],self["navList"],self["navStrListTenDay"]='','','',''
        self["navStrListOneMonth"],self["navStrListThreeMonth"],self["navStrListSixMonth"],self["navStrListOneYear"]='','','',''
        self["navStrListTwoYears"], self["navStrListThreeYears"], self["navStrListFiveYears"], self["navStrListJnylDay"] = '', '', '', ''
        self["jlbdStrList"], self["jlbdStrList"],self["jlbdStrList"],self["manager_code"]='','','',''
        self["company_code"],self["jjjc"],self["jjdm"],self["jjqc"]='','','',''
        self["jjlx"], self["clrq"], self["jjzt"], self["jyzt"] = '', '', '', ''
        self["jjgs"], self["jjjl"],self["jjglf"],self["jjtgf"]='','','',''
        self["smgm"],self["zxfe"],self["jjdm"],self["jjqc"]='','','',''
        self["jjlx"], self["clrq"], self["tgyh"], self["zxgm"] = '', '', '', ''
        return self



class Manager(scrapy.Item):
    code=scrapy.Field()
    name=scrapy.Field()
    cur_company_code=scrapy.Field()
    cur_company_start=scrapy.Field()
    cur_company_end=scrapy.Field()
    cur_company_dur=scrapy.Field()
    cur_company_funds=scrapy.Field()
    word_status=scrapy.Field()
    total_dur=scrapy.Field()
    new_company=scrapy.Field()
    ts=scrapy.Field()
    status=scrapy.Field()

    def getInstance(self):
        self["code"],self["name"],self["cur_company_start"],self["cur_company_end"]='','','',''
        self["cur_company_dur"], self["cur_company_funds"], self["total_dur"], self["new_company"] = '', '', '', ''
        self["ts"], self["status"],self["cur_company_code"],self["word_status"]='','','',''
        return self



