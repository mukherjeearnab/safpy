from typing import Tuple, Any, Union
import jpype
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


def update_state_tuple(state_tuple: Tuple[Any], variable: str, value: Any, var_registry: VariableRegistry) -> Tuple[Any]:
    '''
    Update the State Tuple with the given value of the variable
    '''

    # convert the tuple to a list
    state_tuple = list(state_tuple)

    # get the index of the variable in state tuple
    variable_index = var_registry.get_id(variable)

    # update the state tuple with the given value of the variable
    state_tuple[variable_index] = value

    # return the updated state tuple
    return tuple(state_tuple)


def compute_expression_object(node: Node, var_registry: VariableRegistry, const_registry: VariableRegistry,
                              abstract_state: jpype.JClass, manager: jpype.JClass) -> int:
    '''
    Recursively Compute the Expression Object and return the value
    '''

    MpqScalar = jpype.JClass("apron.MpqScalar")
    Linterm0 = jpype.JClass("apron.Linterm0")
    Linexpr0 = jpype.JClass("apron.Linexpr0")
    Texpr0CstNode = jpype.JClass("apron.Texpr0CstNode")
    Texpr0Node = jpype.JClass("apron.Texpr0Node")
    Texpr0Intern = jpype.JClass("apron.Texpr0Intern")
    Texpr0DimNode = jpype.JClass("apron.Texpr0DimNode")

    # base case: if node type is a Literal, return the value
    if node.node_type == 'Literal':
        return Texpr0CstNode(MpqScalar(int(node.value)))

    # base case: if node type is a Identifier,
    # retrieve the value from var_registry or const_registry
    if node.node_type == 'Identifier':
        if node.name in var_registry.variable_table.keys():
            return Texpr0DimNode(var_registry.get_id(node.name))
        elif node.name in const_registry.variable_table.keys():
            return Texpr0CstNode(MpqScalar(int(const_registry.get_value(node.name))))
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


def compute_binary_operation(left: int, right: int, operator: str, abstract_state: jpype.JClass, manager: jpype.JClass) -> int:
    '''
    Compute a binary operation equation based on the lhs, rhs and operator
    '''
    Texpr0BinNode = jpype.JClass("apron.Texpr0BinNode")

    # Define a mapping from operators to Texpr0BinNode constants
    arithmetic_op_mapping = {
        '+': Texpr0BinNode.OP_ADD,
        '-': Texpr0BinNode.OP_SUB,
        '*': Texpr0BinNode.OP_MUL,
        '/': Texpr0BinNode.OP_DIV
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
        return Texpr0BinNode(arithmetic_op_mapping[operator], left, right)
    elif operator in logical_op_mapping:
        Texpr0Intern = jpype.JClass("apron.Texpr0Intern")

        # Evaluate expressions to get their intervals within the abstract state
        interval_left = abstract_state.getBound(manager, Texpr0Intern(left))
        interval_right = abstract_state.getBound(manager, Texpr0Intern(right))

        # Perform comparison based on the operator
        comparison_result = compare_intervals(
            interval_left, interval_right, operator)

        return comparison_result
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def compare_intervals(interval_left, interval_right, operator):
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


def set_var_registry_state(state: Tuple[Any], variable_reg: VariableRegistry) -> VariableRegistry:
    '''
    Generate a new variable registry containing the state of variables as supplied in the state tuple
    '''

    for variable in variable_reg.variable_table.keys():
        value = state[variable_reg.get_id(variable)]
        variable_reg.set_value(variable, value)

    return variable_reg


def generate_undef_state(variable_reg: VariableRegistry, manager: jpype.JClass) -> Tuple[Any]:
    '''
    Generate the initial abstract state tuple based on
    the variables present in the variable registry
    '''

    # Import APRON Classes
    Abstract0 = jpype.JClass("apron.Abstract0")
    Interval = jpype.JClass("apron.Interval")

    # obtain the variable names and init the state tuple
    variables = variable_reg.variable_table.keys()
    int_variables_count = len(variables)
    real_variables_count = 0

    # init the Inverval for every variable
    # box_state = [Interval() for _ in variables]
    box_state = Interval[int_variables_count]
    for i in range(int_variables_count):
        box_state[i] = Interval()

    # generate the level 0 abstract state
    state = Abstract0(manager, int_variables_count,
                      real_variables_count, box_state)

    return state