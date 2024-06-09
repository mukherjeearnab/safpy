'''
VariableDeclarationStatement Expression Handlers
'''
from typing import Set
from control_flow_graph.node_processor.nodes import VariableDeclarationStatement


def get_variables(node: VariableDeclarationStatement) -> Set[str]:
    '''
    Recursively obtain variables from LHS of the variable declaration
    '''

    left_symbols = set()

    # obtain the left hand assignment symbol
    left = node.declarations[0].name
    # add the assignment to the set of symbols
    left_symbols.add(left)

    return left_symbols
