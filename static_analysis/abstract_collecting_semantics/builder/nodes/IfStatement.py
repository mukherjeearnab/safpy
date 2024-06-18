'''
WhileStatement Expression Handlers
'''
from typing import Set, Tuple, Any, Dict
from copy import deepcopy
import jpype
from static_analysis.abstract_collecting_semantics.objects import VariableRegistry
from control_flow_graph.node_processor.nodes import IfStatement
from static_analysis.abstract_collecting_semantics.builder.common import compute_expression_object, set_var_registry_state


def get_variables(node: IfStatement) -> Set[str]:
    '''
    Recursively obtain variables from LHS of the while statement
    '''

    # as of now, we return empty set
    left_symbols = set()

    return left_symbols


def generate_exit_sets(node: IfStatement, entry_set: Set[Tuple[Any]],
                       var_registry: VariableRegistry, const_registry: VariableRegistry,
                       manager: jpype.JClass) -> Dict[str, Set[Tuple[Any]]]:
    '''
    Function to compute the exit set(s) from the given entry set and node semantics
    '''

    # obtain the condition property
    condition = node.condition

    # obtain the true and false branches
    true_branch = node.true_body_next
    false_branch = node.false_body_next

    Abstract0 = jpype.JClass("apron.Abstract0")

    # init exit_set ('*') as empty set
    exit_dict = {true_branch: Abstract0(manager, entry_set),
                 false_branch: Abstract0(manager, entry_set)}

    #   1. based on the state values, compute the expression
    expr_value = compute_expression_object(
        condition, var_registry, const_registry,
        entry_set, manager)

    #   2. based on the computed expression,
    # if expr_value is True, add state to true branch
    # else add state to false branch
    if expr_value == True:
        exit_dict[true_branch] = entry_set
    elif expr_value == False:
        exit_dict[false_branch] = entry_set
    else:
        raise Exception(
            f'Invalid expression value {expr_value} for If Statement!')

    return exit_dict
