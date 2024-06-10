'''
ExpressionStatement Expression Handlers
'''
from typing import Set, Tuple, Any, Dict
from copy import deepcopy
from static_analysis.collecting_semantics.objects import VariableRegistry
from control_flow_graph.node_processor.nodes import ExpressionStatement
from static_analysis.collecting_semantics.builder.common import traverse_expression_object, update_state_tuple, compute_expression_object


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
                       var_registry: VariableRegistry, const_registry: VariableRegistry) -> Dict[str, Set[Tuple[Any]]]:
    '''
    Function to compute the exit set(s) from the given entry set and node semantics
    '''

    # obtain the expression property
    expression = node.expression

    # init symbol sets
    left_symbol = get_variables(node).pop()

    # init exit_set ('*') as empty set
    exit_set = set()
    # for each state tuple in entry set,
    for state_tuple in entry_set:
        # add the state tuple in the exit set
        exit_set.add(deepcopy(state_tuple))

        # compute the expression,
        expr_value = compute_expression_object(
            expression.leftHandSide, var_registry, const_registry)

        # create a copy of the entry set state tuple
        new_state_tuple = deepcopy(state_tuple)

        # replace the lhs variable's value in the tuple
        new_state_tuple = update_state_tuple(
            new_state_tuple, left_symbol, expr_value, var_registry)

        # add this newly generated tuple to exit set
        exit_set.add(new_state_tuple)

    return {'*': exit_set}
