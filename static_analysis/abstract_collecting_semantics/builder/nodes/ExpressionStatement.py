'''
ExpressionStatement Expression Handlers
'''
from typing import Set, Tuple, Any, Dict
from copy import deepcopy
import jpype
from static_analysis.abstract_collecting_semantics.objects import VariableRegistry
from control_flow_graph.node_processor.nodes import ExpressionStatement
from static_analysis.abstract_collecting_semantics.builder.common import traverse_expression_object, update_state_tuple, compute_expression_object, set_var_registry_state


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

    # handle UnaryOperation nodes
    if expression.node_type == 'UnaryOperation':
        # traverse and generate the left hand side
        traverse_expression_object(
            expression.subExpression, left_symbols)

        return left_symbols
    # can we moe this if else thingy to a class / module based calling method?
    # this will really get complicated with more functionality being added


def generate_exit_sets(node: ExpressionStatement, entry_set: Set[Tuple[Any]],
                       var_registry: VariableRegistry, const_registry: VariableRegistry,
                       manager: jpype.JClass) -> Dict[str, Set[Tuple[Any]]]:
    '''
    Function to compute the exit set(s) from the given entry set and node semantics
    '''

    # obtain the expression property
    expression = node.expression

    print(entry_set)

    Texpr0Intern = jpype.JClass("apron.Texpr0Intern")

    # init symbol sets
    left_symbol = get_variables(node).pop()

    #   1. based on the state values, compute the expression
    expr = compute_expression_object(
        expression.rightHandSide, var_registry, const_registry,
        entry_set, manager)

    # Assuming parsed_expression returns a Texpr0Node or similar
    expr = Texpr0Intern(expr)

    #   2. replace the computed variable (lhs) value in this particular state
    variable_index = var_registry.get_id(left_symbol)
    new_state = entry_set.assignCopy(manager, variable_index, expr, None)

    #   3. add this new state to the set of exit states
    return {'*': new_state}
