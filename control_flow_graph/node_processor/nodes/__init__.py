'''
The Nodes Module

Provides the class definition of different CFG (AST) nodes
'''

from control_flow_graph.helpers import CFGMetadata, Node, BasicBlockTypes, ExtraNodes

# AST Node Types
from control_flow_graph.node_processor.nodes.ContractDefinition import ContractDefinition
from control_flow_graph.node_processor.nodes.ExpressionStatement import ExpressionStatement
from control_flow_graph.node_processor.nodes.FunctionDefinition import FunctionDefinition
from control_flow_graph.node_processor.nodes.IfStatement import IfStatement
from control_flow_graph.node_processor.nodes.PragmaDirective import PragmaDirective
from control_flow_graph.node_processor.nodes.SourceUnit import SourceUnit
from control_flow_graph.node_processor.nodes.VariableDeclaration import VariableDeclaration
