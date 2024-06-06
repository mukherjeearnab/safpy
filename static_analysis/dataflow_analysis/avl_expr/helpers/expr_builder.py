from control_flow_graph.node_processor import Node
from control_flow_graph.node_processor.nodes import ExpressionStatement, VariableDeclarationStatement
from static_analysis.dataflow_analysis.avl_expr.helpers.expr_obj import ExpressionStatement


def build_variable_declaration(vardec_obj: VariableDeclarationStatement) -> ExpressionStatement:
    '''
    Recursively build the variable declaration object
    '''

    left_symbols, right_symbols = set(), set()

    # obtain the left hand assignment symbol
    left = vardec_obj.declarations[0].name
    # add the assignment to the set of symbols
    left_symbols.add(left)

    # if there is an initial value, traverse the right hand assignment
    if vardec_obj.initialValue is not None:
        # traverse and generate the right hand assignment
        right = traverse_expression_object(
            vardec_obj.initialValue, right_symbols)

        # generate the overall expression stmt
        expr_str = f'{left} = {right}'

        # create the expression object
        expr = ExpressionStatement(expr_str, left, right,
                                   left_symbols, right_symbols)

        return expr
    else:
        # in this case, the expression stmt, and the right will be null
        expr = ExpressionStatement('', left, '',
                                   left_symbols, right_symbols)

        return expr


def build_expression(expr_obj: ExpressionStatement) -> ExpressionStatement:
    '''
    Recursively build the expression object
    '''

    # obtain the expression property
    expression = expr_obj.expression

    # init symbol sets
    left_symbols, right_symbols = set(), set()

    # handle assignment nodes
    if expression.node_type == 'Assignment':
        # traverse and generate the left hand side
        left = traverse_expression_object(
            expression.leftHandSide, left_symbols)

        # traverse and generate the right hand side
        right = traverse_expression_object(
            expression.rightHandSide, right_symbols)

        # render the expression
        expr_str = f'{left} {expression.operator} {right}'

        # create the expression object
        expr = ExpressionStatement(expr_str, left, right,
                                   left_symbols, right_symbols)

        return expr


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
