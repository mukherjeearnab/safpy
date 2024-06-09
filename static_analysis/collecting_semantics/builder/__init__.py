'''
The Builder Module for Collecting Semantics
'''

from typing import Set
from control_flow_graph.node_processor import Node
import static_analysis.collecting_semantics.builder.nodes as nodes


def get_variables(node: Node) -> Set[str]:
    '''
    Function to obtain the variables from expressions node-wise 
    '''

    node_module = getattr(nodes, node.node_type, None)

    if node_module is None:
        return set()

    return node_module.get_variables(node)
