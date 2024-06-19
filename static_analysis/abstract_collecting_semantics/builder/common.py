from typing import Tuple, Any, Union
from java_wrapper import java, apron
from static_analysis.abstract_collecting_semantics.objects import VariableRegistry
from control_flow_graph.node_processor import Node


def traverse_expression_object(node: Node, identifiers: set) -> str:
    '''
    Recursively traverse the expression node and generate the expression
    '''

    # base case: if node type is a Literal, return the value
    if node.node_type == 'Literal':
        return str(node.value)

    # base case: if node type is a Identifier, return the name
    if node.node_type == 'Identifier':
        identifiers.add(node.name)
        return node.name

    # handle if node type is Assignment
    if node.node_type == 'Assignment':
        return f'{traverse_expression_object(node.leftHandSide, identifiers)} {node.operator} {traverse_expression_object(node.rightHandSide, identifiers)}'

    # handle if node type is BinaryOperation
    if node.node_type == 'BinaryOperation':
        return f'{traverse_expression_object(node.leftExpression, identifiers)} {node.operator} {traverse_expression_object(node.rightExpression, identifiers)}'


def compute_expression_object(node: Node, var_registry: VariableRegistry, const_registry: VariableRegistry,
                              abstract_state: apron.Abstract0, manager: apron.Manager) -> Union[apron.Texpr0Node, bool]:
    '''
    Recursively Compute the Expression Object and return the value
    '''

    # base case: if node type is a Literal, return the value
    if node.node_type == 'Literal':
        return apron.Texpr0CstNode(apron.MpqScalar(int(node.value)))

    # base case: if node type is a Identifier,
    # retrieve the value from var_registry or const_registry
    if node.node_type == 'Identifier':
        if node.name in var_registry.variable_table.keys():
            return apron.Texpr0DimNode(var_registry.get_id(node.name))
        elif node.name in const_registry.variable_table.keys():
            const_value = const_registry.get_value(node.name)
            if isinstance(const_value, str):
                return apron.Texpr0CstNode(apron.MpqScalar(int(const_value)))
            elif isinstance(const_value, tuple) and len(const_value) == 2:
                return apron.Texpr0CstNode(apron.Interval(int(const_value[0]), int(const_value[1])))
            else:
                raise Exception(
                    f'Illegal value for Constant {node.name}! Value: {const_value}')
        else:
            raise Exception(
                f'Variable {node.name} not found in var or const registry!')

    # handle if node type is BinaryOperation
    if node.node_type == 'BinaryOperation':
        left = compute_expression_object(
            node.leftExpression, var_registry, const_registry, abstract_state, manager)
        right = compute_expression_object(
            node.rightExpression, var_registry, const_registry, abstract_state, manager)

        return compute_binary_operation(left,
                                        right,
                                        node.operator,
                                        abstract_state, manager)

    raise Exception(
        f'Handlers for node type {node.node_type} not implemented yet!')


def compute_binary_operation(left: apron.Texpr0Node, right: apron.Texpr0Node, operator: str,
                             abstract_state: apron.Abstract0, manager: apron.Manager) -> Union[apron.Texpr0BinNode, bool]:
    '''
    Compute a binary operation equation based on the lhs, rhs and operator
    '''
    # Define a mapping from operators to Texpr0BinNode constants
    arithmetic_op_mapping = {
        '+': apron.Texpr0BinNode.OP_ADD,
        '-': apron.Texpr0BinNode.OP_SUB,
        '*': apron.Texpr0BinNode.OP_MUL,
        '/': apron.Texpr0BinNode.OP_DIV
    }

    logical_op_mapping = {
        '==': None,
        '!=': None,
        '<': None,
        '<=': None,
        '>': None,
        '>=': None
    }

    if operator in arithmetic_op_mapping:
        return apron.Texpr0BinNode(arithmetic_op_mapping[operator], left, right)
    elif operator in logical_op_mapping:
        # Evaluate expressions to get their intervals within the abstract state
        interval_left = abstract_state.getBound(
            manager, apron.Texpr0Intern(left))
        interval_right = abstract_state.getBound(
            manager, apron.Texpr0Intern(right))

        # Perform comparison based on the operator
        comparison_result = compare_intervals(
            interval_left, interval_right, operator)

        return comparison_result
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def compare_intervals(interval_left: apron.Interval, interval_right: apron.Interval, operator: str) -> bool:
    # Perform comparison using Interval class methods
    if operator == "==":
        return interval_left.isEqual(interval_right)
    elif operator == "<":
        return interval_left.sup().cmp(interval_right.inf()) < 0
    elif operator == ">":
        return interval_left.inf().cmp(interval_right.sup()) > 0
    elif operator == "<=":
        return interval_left.sup().cmp(interval_right.inf()) <= 0
    elif operator == ">=":
        return interval_left.inf().cmp(interval_right.sup()) >= 0
    elif operator == "!=":
        return not interval_left.isEqual(interval_right)
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def generate_undef_state(variable_reg: VariableRegistry, manager: apron.Manager) -> apron.Abstract0:
    '''
    Generate the initial abstract state tuple based on
    the variables present in the variable registry
    '''

    # obtain the variable names and init the state tuple
    variables = variable_reg.variable_table.keys()
    int_variables_count = len(variables)
    real_variables_count = 0

    # init the Inverval for every variable
    # box_state = [Interval() for _ in variables]
    box_state = apron.Interval[int_variables_count]
    for i in range(int_variables_count):
        box_state[i] = apron.Interval()

    # generate the level 0 abstract state
    state = apron.Abstract0(manager, int_variables_count,
                            real_variables_count, box_state)

    return state
