# -*- coding: utf-8 -*-

import pymongo
import json
from scrapy.conf import settings

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Start_Urls(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION_BAIKE']]
        
    def getStartUrls(self):
        mandict = []
        manlist = self.collection.find({'tag':{'$in':['人物']}})
        for data in manlist:
            if data['infobox'] != None:
                for item in data['infobox'].keys():
                    search_url = "https://zhidao.baidu.com/search?word=" + data['title'] + " " + item
                    mandict.append(search_url)

        return mandict