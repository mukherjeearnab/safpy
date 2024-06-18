'''
VariableDeclarationStatement Expression Handlers
'''
from typing import Set, Tuple, Any, Dict
from copy import deepcopy
import jpype
from static_analysis.abstract_collecting_semantics.objects import VariableRegistry
from control_flow_graph.node_processor.nodes import VariableDeclarationStatement
from static_analysis.abstract_collecting_semantics.builder.common import update_state_tuple, compute_expression_object, set_var_registry_state


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


def generate_exit_sets(node: VariableDeclarationStatement, entry_set: Set[Tuple[Any]], exit_sets: dict,
                       var_registry: VariableRegistry, const_registry: VariableRegistry,
                       manager: jpype.JClass) -> Dict[str, Set[Tuple[Any]]]:
    '''
    Function to compute the exit set(s) from the given entry set and node semantics
    '''

    # init symbol sets
    left_symbol = get_variables(node).pop()

    Abstract0 = jpype.JClass("apron.Abstract0")
    Texpr0Intern = jpype.JClass("apron.Texpr0Intern")

    # EDGE CASE: if the variable is not declared with any values
    if node.initialValue is None:
        return {'*': Abstract0(manager, entry_set)}

    #   1. based on the state values, compute the expression
    expr = compute_expression_object(
        node.initialValue, var_registry, const_registry,
        entry_set, manager)

    # Assuming parsed_expression returns a Texpr0Node or similar
    expr = Texpr0Intern(expr)

    #   2. replace the computed variable (lhs) value in this particular state
    variable_index = var_registry.get_id(left_symbol)
    new_state = entry_set.assignCopy(manager, variable_index, expr, None)

    #   3. add this new state to the set of exit states
    return {'*': new_state}
