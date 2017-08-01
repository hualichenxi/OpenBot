#!/usr/bin/python
# coding=utf-8

from pymongo import MongoClient
import codecs
import cPickle
from collections import defaultdict

client = MongoClient("127.0.0.1", 27017)
db = client['baidubaike2']
collection_work = db['work']
collection_people = db['baike']
db2 = client['baidubaike']
new_collection_entity = db2['entity']
new_collection_cvt = db2['cvt']

new_collection_entity.drop()
new_collection_cvt.drop()

## Entity
id_entity = {}
entity_id = {}
id = 0
occrs = set()
for item in collection_people.find():
    title = item['title']
    if (title, 'people') in occrs:
        continue
    else:
        occrs.add((title, 'people'))
    
    id += 1
    id_entity[id] = title
    entity_id[(title, 'people')] = id

occrs = set()
for item in collection_work.find():
    title = item['title']
    if (title, 'work') in occrs:
        continue
    else:
        occrs.add((title, 'work'))
    id += 1

    id_entity[id] = title
    entity_id[(title, 'work')] = id

    roles_desc = item['roles_desc']
    if roles_desc != None:
        for role_desc in roles_desc:
            role = role_desc['role'][0]
            if type(role) == list:
                role = role[0]
            if (role, 'role') in occrs:
                continue
            else:
                occrs.add((role, 'role'))
            id += 1
            id_entity[id] = role
            entity_id[(role, 'role')] = id

cPickle.dump(id_entity, open('id_entity.pkl', 'w'))
cPickle.dump(entity_id, open('entity_id.pkl', 'w'))
id_entity = cPickle.load(open('id_entity.pkl', 'r'))
entity_id = cPickle.load(open('entity_id.pkl', 'r'))
print('Finish getting map from entity to id')


## CVT
occrs = set()
people_cvt = defaultdict(set)
work_cvt = defaultdict(set)
role_cvt = defaultdict(set)
id = 0
for item in collection_work.find():
    title = item['title']
    if title in occrs:
        continue
    else:
        occrs.add(title)
    roles_desc = item['roles_desc']
    
    if roles_desc != None:
        for role_desc in roles_desc:
            try:
                role = role_desc['role'][0]
                if type(role) == list:
                    role = role[0]
                role = entity_id[(role, 'role')]
            except Exception, e:
                role = None
            try:
                actor = role_desc['actor'][0]
                if type(actor) == list:
                    actor = actor[0]
                actor = entity_id[(actor, 'people')]
            except Exception, e:
                actor = None


            if role != None and actor != None:
                id += 1
                cvt = {"id":id, 'relation':{}}
                cvt['relation']['work'] = entity_id[(title, 'work')]
                cvt['relation']['role'] = role
                cvt['relation']['actor'] = actor
                new_collection_cvt.insert(cvt)
                people_cvt[actor].add(id)
                work_cvt[entity_id[(title, 'work')]].add(id)
                role_cvt[role].add(id)

# cPickle.dump(people_cvt, open('people_cvt.pkl', 'w'))
# cPickle.dump(work_cvt, open('work_cvt.pkl', 'w'))
# cPickle.dump(role_cvt, open('role_cvt.pkl', 'w'))
# people_cvt = cPickle.load(open('people_cvt.pkl', 'r'))
# work_cvt = cPickle.load(open('work_cvt.pkl', 'r'))
# role_cvt = cPickle.load(open('role_cvt.pkl', 'r'))
print('Finish getting cvt information')

## Entity
occrs = set()
for item in collection_people.find():
    title = item['title']
    if title in occrs:
        continue
    else:
        occrs.add(title)
    new_item = {}
    new_item['id'] = entity_id[(title, 'people')]
    new_item['title'] = title
    new_item['infobox'] = item['infobox']
    if new_item['infobox'] == None:
        new_item['infobox'] = {}
    try:
        new_item['infobox']['作品'] = list(people_cvt[new_item['id']])
    except Exception, e:
        new_item['infobox']['作品'] = None
    new_item['type'] = 'people'
    new_collection_entity.insert(new_item)

occrs = set()
for item in collection_work.find():
    title = item['title']
    new_item = {}
    new_item['id'] = entity_id[(title, 'work')]
    if title in occrs:
        continue
    else:
        occrs.add(title)
    new_item['title'] = title
    new_item['infobox'] = item['infobox']
    if new_item['infobox'] == None:
        new_item['infobox'] = {}
    try:
        new_item['infobox']['演员'] = list(work_cvt[new_item['id']])
    except Exception, e:
        new_item['infobox']['演员'] = None
    new_item['type'] = 'work'
    new_collection_entity.insert(new_item)
    roles_desc = item['roles_desc']
    if roles_desc != None:
        for role_desc in roles_desc:
            role = role_desc['role']
            role = role_desc['role'][0]
            if type(role) == list:
                role = role[0]
            if role in occrs:
                continue
            else:
                occrs.add(role)
            role_item = {'id':entity_id[(role, 'role')], 'title':role, 'infobox':{u'出现': list(role_cvt[entity_id[(role, 'role')]])}, 'type':'role'}
            # try:
            #     role_item['infobox']['出现在'] = list(role_cvt[entity_id[title]])
            # except Exception, e:
            #     role_item['infobox']['出现在'] = None
            new_collection_entity.insert(role_item) 

print("Finishing getting entity information")