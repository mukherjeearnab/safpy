'''
ExpressionStatement Expression Handlers
'''
from typing import Set, Tuple, Any, Dict
from copy import deepcopy
from static_analysis.collecting_semantics.objects import VariableRegistry
from control_flow_graph.node_processor.nodes import ExpressionStatement
from static_analysis.collecting_semantics.builder.common import traverse_expression_object


def get_variables(node: ExpressionStatement) -> Set[str]:
    '''
    Recursively obtain variables from LHS of the expression
    '''

    # obtain the expression property
    expression = node.expression

    # init symbol sets
    left_symbols = set()

    # handle assignment nodes
    if expression.node_type == 'Assignment':
        # traverse and generate the left hand side
        traverse_expression_object(
            expression.leftHandSide, left_symbols)

        return left_symbols


def generate_exit_sets(node: ExpressionStatement, entry_set: Set[Tuple[Any]],
                       var_registry: VariableRegistry, const_registry: VariableRegistry) -> Dict[Set[Tuple[Any]]]:
    '''
    Function to compute the exit set(s) from the given entry set and node semantics
    '''

    # init exit_set ('*') as empty set
    exit_set = set()
    # for each state tuple in entry set,
    # add the state tuple in the exit set
    # compute the expression,
    # create a copy of the entry set state tuple,
    # replace the lhs variable's value in the tuple
    # add this newly generated tuple to exit set
