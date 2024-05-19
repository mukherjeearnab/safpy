'''
The Nodes Module

Provides the class definition of different CFG (AST) nodes
'''

from typing import Union
from enum import Enum

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
