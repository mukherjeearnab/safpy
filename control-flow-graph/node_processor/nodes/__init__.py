'''
The Nodes Module

Provides the class definition of different CFG (AST) nodes
'''

from typing import Union

extra_nodes = {
    'condition': {
        'CN_F': 'ForLoop_Condition',
        'CN_W': 'WhileLoop_Condition',
        'CN_DW': 'DoWhileLoop_Condition'
    },
    'join': {
        'JN_F': 'ForLoop_Join',
        'JN_W': 'WhileLoop_Join',
        'JN_DW': 'DoWhileLoop_Join',
        'JN_IF': 'IfCOndition_Join'
    },
    'entry': {
        'EN_DW': 'DoWhileLoop_Entry'
    }
}


class Node(object):
    '''
    Base class for nodes
    '''

    def __init__(self, ast_node: Union[dict, str], prev_node_id: str, join_node_id: str,
                 cfg_metadata: object):
        '''
        Constructor
        '''

        self.entry_node = self
        self.exit_node = self

        self.next_node = None
        self.previous_node = None

        self.children = []

