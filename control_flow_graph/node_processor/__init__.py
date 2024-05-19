'''
The Node Processor Sub-module

Provides logic for node types and their class methods.
Also contains the logic to traverse the AST to generate the CFG.
'''
from enum import Enum
from collections import defaultdict
from control_flow_graph.node_processor.nodes import Node


class BasicBlockTypes(Enum):
    Entry = 'Entry_Block'
    Exit = 'Exit_Block'

    Statement = 'Statement_Block'
    FunctionBody = 'FunctionBody_Block'
    ClassBody = 'ClassBody_Block'

    Conditional = 'Conditional_Block'
    Loop = 'LoopBlock'
    Branch = 'Branch_Block'

    FunctionCall = 'FunctionCall_Block'


class CFGMetadata(object):
    '''
    Metadata Container Class Definition
    '''

    def __init__(self):
        self.node_table = dict()
        self.node_count = defaultdict(int)

    def register_node(self, node_pointer: Node, node_type: str) -> str:
        '''
        Register and Return the Node's Given ID
        '''

        node_id = f'{node_type}_{self.node_count[node_type]}'
        self.node_count[node_type] += 1

        self.node_table[node_id] = node_pointer

        return node_id
