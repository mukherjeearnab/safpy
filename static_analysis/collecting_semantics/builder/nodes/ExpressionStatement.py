'''
ExpressionStatement Expression Handlers
'''
from typing import Set
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
