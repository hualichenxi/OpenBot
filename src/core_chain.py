#!/usr/bin/python
# coding=utf-8

from copy import deepcopy
import sys
sys.path.append('..')
from kb.KBInterface import KBInterface

'''
Basic structure for the core chain
'''

class Edge(object):
    '''
    Edge in the core chain
    '''
    def __init__(self, relation, srcNode, dstNode):
        self.relation = relation
        self.srcNode = srcNode
        self.dstNode = dstNode

class Node(object):
    '''
    Node in the core chain
    '''
    def __init__(self, entity=None):
        self.entity=entity
    def display(self):
        raise NotImplementedError()

class GroundEntityNode(Node):
    '''
    Ground entity node in the core chain
    '''
    def __init__(self, entity, id = -1, edge_next = None):
        Node.__init__(self, entity)
        self.is_cvt = False
        self.id = id
    
    def display(self):
        print(self.entity)

class ExistentialVariableNode(Node):
    '''
    Existential Variable Node in the core chain
    '''
    def __init__(self, entity=None, edge_constraints=None,\
        edge_aggregations=None, id=-1, is_cvt=False):
        Node.__init__(self, entity)
        if edge_constraints != None:
            self.constraints = edge_constraints
        else:
            self.constraints = set()
        if edge_aggregations != None:
            self.aggregations = edge_aggregations
        else:
            self.aggregations = set()
        self.is_cvt = is_cvt
        self.id = id
    
    def display(self):
        print("id: {iid}, is_cvt: {is_cvt}".format(iid=self.id, is_cvt=self.is_cvt))
    
    def add_constraint(self, constraint):
        self.constraints.add(constraint)
    
    def add_aggregation(self, aggregation):
        self.aggregations.add(aggregation)
    

class LambdaVariableNode(Node):
    '''
    Lambda variable node in the core chain
    '''
    def __init__(self, entity=None):
        Node.__init__(self, entity)

    def display(self):
        print('Lambda')

class AggreFuncNode(Node):
    '''
    Aggregation function node in the core chain
    '''
    def __init__(self, entity=None, is_aggr=True):
        Node.__init__(self, entity)
        self.is_aggr = is_aggr
    
    def display(self):
        print('Aggre')

## State transform table
state_actions = {\
    'phi':{'Ae':'Se'},\
    'Se':{'Ap':'Sp'},\
    'Sp':{'Aa':'Sc', 'Ac':'Sc'},\
    'Sc':{'Aa':'Sc', 'Ac':'Sc'},\
}

## KB query interface
kb = KBInterface()

MAX_AGGREGATION_CNT = 0
MAX_CONSTRAINT_CNT = 0

class CoreChain(object):
    '''
    Core chain
    '''
    def __init__(self, s):
        self.nodes = []
        self.s = s
        self.state = 'phi'
        self.aggregation_cnt = 0
        self.constraint_cnt = 0
    
    def set_state(self, state):
        self.state = state
    
    def add_node(self, node):
        self.nodes.append(node)
    
    def add_constraint(self, ind, constraint):
        self.nodes[ind].add_constraint(constraint)
    
    def add_aggregation(self, ind, aggregation):
        self.nodes[ind].add_aggregation(aggregation)
    
    def get_last_node(self):
        assert len(self.nodes) > 0
        return self.nodes[-1]

    def get_nodes_len(self):
        return len(self.nodes)
    
    def get_existential_nodes(self):
        '''
        get exitential nodes in the core chain
        Returns:
            the index together with the node
        '''
        if len(self.nodes) == 0:
            return None
        return filter(lambda node: type(node[1]) == ExistentialVariableNode, zip(range(len(self.nodes)), self.nodes))
    
    def is_valid(self):
        '''
        Wether the core chain is validate
        '''
        return self.state == 'Sp' or self.state == 'Sc'

    def apply_Ae(self):
        '''
        Apply Ae to the core chain
        Returns:
            A set of new generated core chain
        '''
        assert self.state == 'phi'
        next_state = 'Se'
        res = set()
        entities = kb.get_entities(self.s)
        for entity in entities:
            entity_node = GroundEntityNode(entity=entity, id=entity[0])
            new_core_chain = deepcopy(self)
            new_core_chain.add_node(entity_node)
            new_core_chain.set_state(next_state)
            res.add(new_core_chain)
        return res
    
    def apply_Ap(self):
        '''
        Apply Ap to the core chain 
        '''
        assert self.state == 'Se'
        next_state = 'Sp'
        res = set()
        node = self.get_last_node()

        related_entities = kb.get_related_entities(node)
        for is_cvt, relation, entity in related_entities:
            new_core_chain = deepcopy(self)
            node = ExistentialVariableNode(entity=entity, is_cvt=is_cvt)
            new_core_chain.nodes.append((relation, node))
            new_core_chain.set_state(next_state)
            res.add(new_core_chain)
        
        return res
    
    def apply_Ac(self):
        '''
        Apply Ac tot he core chain
        '''
        assert self.state == 'Sp' or self.state == 'Sc'
        next_state = 'Sc'
        res = set()
        if self.constraint_cnt > MAX_CONSTRAINT_CNT:
            return res
        nodes = self.get_existential_nodes()
        for ind, node in nodes:
            related_entities = kb.get_constraints(node, self.s)
            for related_entity in related_entities:
                new_core_chain = deepcopy(self)
                new_core_chain.add_constraint(ind, related_entities)
                new_core_chain.constraint_cnt += 1
                new_core_chain.set_state(next_state)
                res.add(new_core_chain)

        return res

    def apply_Aa(self):
        '''
        Apply Aa tot he core chain
        '''
        assert self.state == 'Sp' or self.state == 'Sc'
        next_state = 'Sc'
        res = set()
        if self.aggregation_cnt >= MAX_AGGREGATION_CNT:
            return res
        nodes = self.get_existential_nodes()
        for ind, node in nodes:
            aggres = kb.get_aggregations(self.s)
            for aggre in aggres:
                new_core_chain = deepcopy(self)
                new_core_chain.add_aggregation(ind, aggre)
                new_core_chain.set_state(next_state)
                new_core_chain.aggregation_cnt += 1
                res.add(new_core_chain)
        return res
    
    def apply(self, search_filter=None):
        res = set()
        for action in state_actions[self.state].keys():
            if action == 'Ae':
                res.update(self.apply_Ae())
            elif action == 'Ap':
                res.update(self.apply_Ap())
            elif action == 'Ac':
                res.update(self.apply_Ac())
            elif action == 'Aa':
                res.update(self.apply_Aa())
        if search_filter is not None:
            res = search_filter(res) 
        return res

    def display(self):
        '''
        Print the core chain
        '''
        print('------------------')
        for node in self.nodes:
            if type(node) == tuple:
                print(node[0])
                node[1].display()
            else:
                node.display()
        print('------------------')


class CoreChainGenerator(object):
    def __init__(self):
        pass
    
    def beam_filter(self):
        '''
        Beam search filter
        '''
        raise NotImplementedError()

    def generate(self, s):
        '''
        Generate core chains for the specified string
        '''
        current_core_chains = set()
        visited_core_chains = set()
        init_core_chain = CoreChain(s)
        current_core_chains.add(init_core_chain)
        while True:
            res_core_chain = set()
            for core_chain in current_core_chains:
                if core_chain not in visited_core_chains:
                    res_core_chain.update(core_chain.apply())
            visited_core_chains.update(current_core_chains)
            new_added_core_chain = res_core_chain - current_core_chains

            if len(new_added_core_chain) == 0:
                break

            # Add new generated core chain to the current core chains set
            current_core_chains.update(new_added_core_chain)
        # Filter the valid core chains
        current_core_chains = filter(lambda core_chain: core_chain.is_valid(), current_core_chains)

        return current_core_chains
