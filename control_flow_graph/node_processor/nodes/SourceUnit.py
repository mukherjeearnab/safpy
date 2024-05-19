'''
Class definition for the Pragma Directive CFG (AST) node
'''
from typing import Union
from control_flow_graph.node_processor.nodes import BasicBlockTypes
from control_flow_graph.node_processor.nodes import Node


class SourceUnit(Node):
    '''
    Source Unit Node
    '''

    def __init__(self, ast_node: Union[dict, str], prev_node_id: str, join_node_id: str,
                 cfg_metadata: object):
        '''
        Constructor
        '''

        self.basic_block_type = BasicBlockTypes.EntryBlock

        self.entry_node = self
        self.exit_node = self

        self.next_node = None
        self.previous_node = None

        self.children = []
