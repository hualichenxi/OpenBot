#!/usr/bin/python
# coding=utf-8

from pymongo import MongoClient

def filter_constraint(constraint, s):
    '''
    TODO: Implement
    '''
    return constraint

class QueryInterface(object):
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
        for item in self.collection_entity.find({'id':entity_id}):
            if item != None:
                infobox = item['infobox']
                if infobox != None:
                    for key, value in infobox.items():
                        yield (key, value)

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
        for item in self.collection_cvt.find({'id':cvt_id}):
            if item != None:
                relation = item['relation']
                assert relation != None
                if relation != None:
                    for key, value in relation.items():
                        yield (key, value)
    
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
        @param: node: the node where the contraints are to add
        @param: s: the original string
        @param: the constraints list
        '''
        related_entities = self.get_related_entities(node)
        b_filter_constraint = False
        if b_filter_constraint:
            related_entities = filter_constraint(related_entities, s)
        return related_entities
    
    def get_aggregations(self, s):
        '''
        TODO: Implement
        Get the possible aggregation can be added
        @param: s: the original string
        @return: the aggregations list
        '''
        return []
    
    def get_entities(self, s):
        '''
        TODO: Implement
        Get the possible entities in the string
        @param s: the original string
        @return: the entities list
        '''
        return []
