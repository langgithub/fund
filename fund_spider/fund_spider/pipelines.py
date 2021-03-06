# -*- coding: utf-8 -*-
import pymongo
from scrapy import log
from scrapy.conf import settings
import threading
from openpyxl import Workbook
import redis
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# 单例模式创建MongoPiplie

Lock = threading.Lock()
class MongoPipeline(object):

    # 定义静态变量实例
    __instance = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            try:
                Lock.acquire()
                # double check
                if not cls.__instance:
                    cls.client = pymongo.MongoClient(settings['MONGO_URI'])
                    cls.db = cls.client[settings['MONGO_DATABASE']]
                    cls.__instance = super(MongoPipeline, cls).__new__(cls, *args, **kwargs)
            finally:
                Lock.release()
        return cls.__instance

    def process_item(self, item, spider):
        collection_name = item.__class__.__name__
        log.msg("insert {0}".format(collection_name),level=log.INFO)
        self.db[collection_name].insert(dict(item))
        return item

    def process_item(self, item):
        collection_name = item.__class__.__name__
        log.msg("insert {0}".format(collection_name), level=log.INFO)
        self.db[collection_name].insert(dict(item))
        return item

    def company_seed_insert(self,seed):
        return self.db["Company"].insert(seed)

    def company_seed_find(self):
        return self.db["Company"].find({"status": 0}, {"url": 1, "_id": 0})

    def fund_seed_find(self):
        return self.db["Fund"].find({"status": 0}, {"url": 1, "_id": 0}).limit(50)

    def fund_info_update(self,info):
        return self.db["Fund"].update_one({"url":info["url"]},
                                          {"$set":{
                                              "gpzhListData":info["gpzhListData"],
                                              "hyPieData": info["hyPieData"],
                                              "zcPieData": info["zcPieData"],
                                              "jjpmChartData": info["jjpmChartData"],
                                              "navList": info["navList"],
                                              "navStrListTenDay":info["navStrListTenDay"],
                                              "navStrListOneMonth": info["navStrListOneMonth"],
                                              "navStrListThreeMonth": info["navStrListThreeMonth"],
                                              "navStrListSixMonth": info["navStrListSixMonth"],
                                              "navStrListOneYear": info["navStrListOneYear"],
                                              "navStrListTwoYears": info["navStrListTwoYears"],
                                              "navStrListThreeYears": info["navStrListThreeYears"],
                                              "navStrListFiveYears": info["navStrListFiveYears"],
                                              "navStrListJnylDay":info["navStrListJnylDay"],
                                              "jlbdStrList": info["jlbdStrList"],
                                              "manager_code": info["manager_code"],
                                              "company_code": info["company_code"],
                                              "jjjc": info["jjjc"],
                                              "jjdm": info["jjdm"],
                                              "jjqc": info["jjqc"],
                                              "jjlx": info["jjlx"],
                                              "clrq": info["clrq"],
                                              "jjzt": info["jjzt"],
                                              "jyzt": info["jyzt"],
                                              "jjgs": info["jjgs"],
                                              "jjjl": info["jjjl"],
                                              "jjglf": info["jjglf"],
                                              "jjtgf": info["jjtgf"],
                                              "smgm": info["smgm"],
                                              "zxfe": info["zxfe"],
                                              "tgyh": info["tgyh"],
                                              "zxgm": info["zxgm"],
                                              "ts":info["ts"],
                                              "status":info["status"]
                                          }},True)

    def manager_info_seed_find(self):
        return self.db["ManagerInfo"].find({"status":0},{"manager_code": 1, "_id": 0})

    def manager_info_update(self,info):
        log.msg("update ManagerInfo")
        return self.db["ManagerInfo"].update_one({"manager_code":info["manager_code"]},
                                          {"$set":{
                                              "current_company_code":info["current_company_code"],
                                              "current_company_name": info["current_company_name"],
                                              "person_instr": info["person_instr"],
                                              "work_start": info["work_start"],
                                              "work_duration": info["work_duration"],
                                              "work_company_num":info["work_company_num"],
                                              "work_frequency": info["work_frequency"],
                                              "work_fund_num": info["work_fund_num"],
                                              "work_repay_avg": info["work_repay_avg"],
                                              "the_most_repay": info["the_most_repay"],
                                              "the_most_retreat": info["the_most_retreat"],
                                              "ts": info["ts"],
                                              "status": info["status"]
                                          }},True)

    def manager_seed_find(self):
        return self.db["Manager"].find({"status": 0}, {"url": 1, "_id": 0}).limit(50)


#########redis#############################################
class RedisPipeline(object):

    def __init__(self):
        if not hasattr(RedisPipeline, 'pool'):
            RedisPipeline.create_pool()
        self._connection = redis.Redis(connection_pool=RedisPipeline.pool)

    @staticmethod
    def create_pool():
        RedisPipeline.pool = redis.ConnectionPool(
            host="127.0.0.1",
            port=6379,
            db=0)

    def set_lianjia_seed(self, key, value):
        '''''set data with (key, value)
        '''
        return self._connection.lpush(key, value)

    def set_seed(self, key, value):
        '''''set data with (key, value)
        '''
        return self._connection.lpush(key, value)

    def list_len(self,key):
        '''
        获取长度
        :return: 
        '''
        return self._connection.llen(key)


class ExcelPipeline(object):

    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['文章url', '文章title', '文章发布时间', '文章内容', '文章作者连接', '文章作者','文章评论数量'])  # 设置表头

        self.wb2 = Workbook()
        self.ws2 = self.wb2.active
        self.ws2.append(['文章url', '评论人', '评论时间', '评论内容', '评论给那一条', '评论给谁'])  # 设置表头

    def process_item(self, item, spider):
        collection_name = item.__class__.__name__
        if collection_name=="DouBanItem":
            line = [item['article_url'], item['article_title'], item['article_publish_date'], item['article_content']
                , item['article_author_url'],item['article_author_name'],item['article_comment_quantity']]  # 把数据中每一项整理出来
            self.ws.append(line)  # 将数据以行的形式添加到xlsx中
            self.wb.save('content.xlsx')  # 保存xlsx文件
            return item
        if collection_name=="CommentItem":
            line = [item['article_url'], item['comment_people'], item['comment_time'], item['comment_content']
                , item['comment_to_which_coment'],item['comment_to_Who']]  # 把数据中每一项整理出来
            self.ws2.append(line)  # 将数据以行的形式添加到xlsx中
            self.wb2.save('comment.xlsx')  # 保存xlsx文件
            return item
