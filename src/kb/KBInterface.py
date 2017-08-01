#!/usr/bin/python
# coding=utf-8

from pymongo import MongoClient
import sys
sys.path.append('..')
from feature.extract_feature import entity_link

CVT_RELATIONS = set([u'演员', u'出现', u'作品'])

def filter_constraint(constraint, s):
    '''
    TODO: Implement
    '''
    raise NotImplementedError()

class KBInterface(object):
    def __init__(self, db='baidubaike'):
        client = MongoClient("127.0.0.1", 27017)
        self.db = client[db]
        self.collection_entity = self.db['entity']
        self.collection_cvt = self.db['cvt']

    def get_entities_by_name(self, entity_name):
        '''
        Get the entity json description from KB by the entity name
        '''
        items = []
        for item in self.collection_entity.find({'title':entity_name}):
            items.append(item)
        return items

    def get_entity_by_id(self, entity_id):
        '''
        Get the entity json description from KB by the entity id
        '''
        for item in self.collection_entity.find({'id':entity_id}):
            if item != None:
                return item
        return None

    def get_entity_relations(self, entity_id):
        '''
        Get the entity related relation together with its related object from KB
        '''
        res = []
        if entity_id == -1:
            return res
        for item in self.collection_entity.find({'id':entity_id}):
            if item != None:
                infobox = item['infobox']
                if infobox != None:
                    for key, value in infobox.items():
                        if value == None:
                            continue
                        if key in CVT_RELATIONS:
                            for val in value:
                                res.append((True, key, val))
                        else:
                            res.append((False, key, value))
        return res

    def get_cvt_by_id(self, cvt_id):
        '''
        Get the cvt json description from KB by the cvt id
        '''
        for item in self.collection_cvt.find({'id':cvt_id}):
            if item != None:
                return item
        return None
    
    def get_cvt_relations(self, cvt_id):
        '''
        Get the cvt related relation together with its related object from KB
        '''
        res = []
        for item in self.collection_cvt.find({'id':cvt_id}):
            if item != None:
                relation = item['relation']
                assert relation != None
                if relation != None:
                    for key, value in relation.items():
                        res.append((False, key, value))
        return res
    
    def get_related_entities(self, node):
        if node.is_cvt == False:
            related_entities = self.get_entity_relations(node.id)
        else:
            related_entities = self.get_cvt_relations(node.id)
        return related_entities
    
    def get_constraints(self, node, s):
        '''
        Get the possible constraint can be added to the specified node according 
        to the original string
        Args:
            node: the node where the contraints are to add
            s: the original string
        Returns:
            the constraints list
        '''
        related_entities = self.get_related_entities(node)
        b_filter_constraint = False
        if b_filter_constraint:
            related_entities = filter_constraint(related_entities, s)
        return related_entities
    
    def get_aggregations(self, s):
        '''
        Get the possible aggregation can be added
        Args:
            s: the original string
        Return:
            the aggregations list
        '''
        # raise NotImplementedError()
        # Currently having no aggregations
        return []
    
    def get_entities(self, s, conf_threshold=0.4, maxn=10):
        '''
        Get the possible entities in the string
        Args:
            s: the original string
            conf_threshold: the threshold for entity link confidence
            maxn: maximum number of extracted entity
        Returns:
            the entities list
        '''
        entities = entity_link(s)
        # res = filter(lambda x : x[1] >= conf_threshold, res)
        entities = entities[:maxn]

        def get_entity_detail_info(entity_name):
            entities = self.get_entities_by_name(entity_name)
            return [[entity['id'], entity_name] for entity in entities]

        res = set()
        for prop, entity in entities:
            detail_infos = get_entity_detail_info(entity)
            for info in detail_infos:
                res.add((info[0], info[1], prop))

        return res

