'''
VariableDeclarationStatement Expression Handlers
'''
from typing import Set, Tuple, Any, Dict
from copy import deepcopy
from static_analysis.collecting_semantics.objects import VariableRegistry
from control_flow_graph.node_processor.nodes import VariableDeclarationStatement
from static_analysis.collecting_semantics.builder.common import traverse_expression_object, update_state_tuple, compute_expression_object


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


def generate_exit_sets(node: VariableDeclarationStatement, entry_set: Set[Tuple[Any]],
                       var_registry: VariableRegistry, const_registry: VariableRegistry) -> Dict[str, Set[Tuple[Any]]]:
    '''
    Function to compute the exit set(s) from the given entry set and node semantics
    '''

    # init symbol sets
    left_symbol = get_variables(node).pop()

    # init exit_set ('*') as empty set
    exit_set = set()
    # for each state tuple in entry set,
    for state_tuple in entry_set:
        # EDGE CASE: if the variable is not declared with any values
        if node.initialValue is None:
            continue

        # compute the expression,
        expr_value = compute_expression_object(
            node.initialValue, var_registry, const_registry)

        print(node.cfg_id, expr_value, left_symbol)

        # create a copy of the entry set state tuple
        new_state_tuple = deepcopy(state_tuple)

        # replace the lhs variable's value in the tuple
        new_state_tuple, need_to_drop = update_state_tuple(
            new_state_tuple, left_symbol, expr_value, var_registry)

        # also update the value in the variable registry
        var_registry.set_value(left_symbol, expr_value)

        # add the state tuple in the exit set
        if not need_to_drop:
            exit_set.add(deepcopy(state_tuple))

        # add this newly generated tuple to exit set
        exit_set.add(new_state_tuple)

    return {'*': exit_set}
