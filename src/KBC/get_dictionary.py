#!/usr/bin/python
# coding=utf-8

'''
Get the person name together with alias name list and movies/opera works list
'''

from pymongo import MongoClient
import codecs
import re

client = MongoClient("127.0.0.1", 27017)
db = client['baidubaike2']
collection_work = db['work']
collection_people = db['baike']

def filter_title(title):
    '''
    Filter some part in the title.
    For example
    中国人（刘德华演唱的歌曲）  ->   中国人
    '''
    title = re.sub(u'（.*）', u'', title)
    title = re.sub(u'（.*$', u'', title)
    title = re.sub(u'\(.*\)', u'', title)
    title = re.sub(u'\(.*$', u'', title)

    return title

def get_person_name_list():
    person_name_list = set()
    for item in collection_people.find():
        title = item['title']
        title = filter_title(title)
        person_name_list.add(title)

        infobox = item['infobox']
        if infobox == None:
            continue
        ## Name in foreign language
        names = infobox.get(u'外文名', None)
        if names != None:
            if type(names) == list:
                person_name_list.update(names)
            else:
                person_name_list.add(names)
        ## Alias name
        names = infobox.get(u'别名', None)
        if names != None:
            if type(names) == list:
                person_name_list.update(names)
            else:
                person_name_list.add(names)
        ## Chinese name
        names = infobox.get(u'中文名', None)
        if names != None:
            if type(names) == list:
                person_name_list.update(names)
            else:
                person_name_list.add(names)
        
    print('Total person name count %d' % (len(person_name_list)))
    return person_name_list

def get_work_name_list():
    work_name_list = set()
    for item in collection_work.find():
        title = item['title']
        title = filter_title(title)
        work_name_list.add(title)

    print('Total work name count %d' %(len(work_name_list)))
    return work_name_list

if __name__ == '__main__':
    person_name_list = get_person_name_list()
    with codecs.open('person_name_list.txt', 'w', 'utf-8') as f:
        for person_name in person_name_list:
            if type(person_name) == str:
                person_name = person_name.decode('utf-8')
            person_name = filter_title(person_name)
            f.write(person_name)
            f.write('\n')
    work_name_list = get_work_name_list()
    with codecs.open('work_name_list.txt', 'w', 'utf-8') as f:
        for work_name in work_name_list:
            if type(person_name) == str:
                person_name = person_name.decode('utf-8')
            person_name = filter_title(person_name)
            f.write(person_name)
            f.write('\n')