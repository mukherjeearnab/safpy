'''
The Nodes Module

Provides the class definition of different CFG (AST) nodes
'''

from typing import Union
from enum import Enum

from control_flow_graph.node_processor import CFGMetadata

# AST Node Types
from control_flow_graph.node_processor.nodes.ContractDefinition import ContractDefinition
from control_flow_graph.node_processor.nodes.ExpressionStatement import ExpressionStatement
from control_flow_graph.node_processor.nodes.FunctionDefinition import FunctionDefinition
from control_flow_graph.node_processor.nodes.IfStatement import IfStatement
from control_flow_graph.node_processor.nodes.PragmaDirective import PragmaDirective
from control_flow_graph.node_processor.nodes.SourceUnit import SourceUnit
from control_flow_graph.node_processor.nodes.VariableDeclaration import VariableDeclaration


class ExtraNodes(Enum):
    CN_F = 'ForLoop_Condition'
    CN_W = 'WhileLoop_Condition'
    CN_DW = 'DoWhileLoop_Condition'

    JN_F = 'ForLoop_Join'
    JN_W = 'WhileLoop_Join'
    JN_DW = 'DoWhileLoop_Join'
    JN_IF = 'IfCOndition_Join'

    EN_SOURCE = 'SourceUnit_Entry'
    EN_DW = 'DoWhileLoop_Entry'
    EN_FN = 'FunctionBody_Entry'

    EX_FN = 'FunctionBody_Exit'
    EX_SOURCE = 'SourceUnit_Exit'


class Node(object):
    '''
    Base class for nodes
    '''

    def __init__(self, ast_node: Union[dict, str],
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''

        _ = cfg_metadata

        # set the entry node and the exit node
        # entry node is start (global) and exit node is end (global)
        self.entry_node = entry_node_id
        self.exit_node = exit_node_id

        # init next nodes as a list of node ids
        # same goes for previous nodes, but we initially add the previous_node
        # here previous node is the one from which we call this node's constructor
        self.next_nodes = []
        self.previous_nodes = [prev_node_id]

        # also, if a join node is being supplied, apply it
        # this is somewhat similar to how the exit node is propagated
        self.join_node = join_node_id

        # set the source map in the form (s:l:i)
        # s = start index, l = length, i = index
        self.src_map = (int(i) for i in ast_node['src'].split(':'))

        # set the ast id, if available
        self.ast_id = ast_node.get('id', None)

        # set the children nodes from the AST node information
        self.children = ast_node.get('nodes', list())
