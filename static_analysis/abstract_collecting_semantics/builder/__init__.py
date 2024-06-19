'''
The Builder Module for Collecting Semantics
'''

from typing import Set, Tuple, Any, Dict
from copy import deepcopy
from java_wrapper import apron
from control_flow_graph.node_processor import Node
import static_analysis.abstract_collecting_semantics.builder.nodes as nodes
from static_analysis.abstract_collecting_semantics.objects import VariableRegistry


def get_variables(node: Node) -> Set[str]:
    '''
    Function to obtain the variables from expressions node-wise
    '''

    node_module = getattr(nodes, node.node_type, None)

    if node_module is None:
        return set()

    return node_module.get_variables(node)


def generate_exit_sets(node: Node, entry_set: apron.Abstract0, exit_sets: Dict[str, apron.Abstract0],
                       var_registry: VariableRegistry, const_registry: VariableRegistry,
                       manager: apron.Manager) -> Dict[str, apron.Abstract0]:
    '''
    Function to compute the exit set(s) from the given entry set and node semantics
    '''

    node_module = getattr(nodes, node.node_type, None)

    if node_module is None:
        return {'*': apron.Abstract0(manager, entry_set)}

    return node_module.generate_exit_sets(node, entry_set, exit_sets, var_registry, const_registry, manager)
