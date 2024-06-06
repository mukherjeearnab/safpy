'''
The Available Expression DataFlow Analysis
'''

from control_flow_graph import ControlFlowGraph
from static_analysis.dataflow_analysis.avl_expr.helpers.expr_builder import build_expression, build_variable_declaration
from static_analysis.dataflow_analysis.avl_expr.helpers.expr_obj import Expression, ExpressionStatement


class AvailableExpressionAnalysis(object):
    '''
    Class defining the available expression data flow analysis
    '''

    def __init__(self, cfg: ControlFlowGraph, starting_node: str, ending_node: str):
        '''
        Constructor
        '''

        self.cfg = cfg
        self.starting_node = starting_node
        self.ending_node = ending_node

        self.GEN = dict()
        self.KILL = dict()

        self.ENTRY = dict()
        self.EXIT = dict()

        self.expr_table = dict()
        self.node_expr_table = dict()

    def set_node_expr(self, node_id: str, expr: ExpressionStatement) -> None:
        '''
        Add Node's ExpressionStatement to the table
        '''

        self.node_expr_table[node_id] = expr

    def get_node_expr(self, node_id: str) -> ExpressionStatement:
        '''
        Get Node's ExpressionStatement from the table
        '''

        return self.node_expr_table[node_id]

    def set_expr(self, expr_str: str, symbols: set) -> None:
        '''
        Add Expression to expression table
        '''

        expr = Expression(expr_str, symbols)

        self.expr_table[expr.expression] = expr

    def get_expr(self, expr_str: str) -> Expression:
        '''
        Get Expression from expression table
        '''

        return self.expr_table[expr_str]

    def get_exprs_with_symbol(self, symbol: str) -> str:
        '''
        Get Expression(s) having symbol from expression table
        '''

        list_of_expressions = []
        for _, expr in self.expr_table.items():
            if symbol in expr.symbols:
                list_of_expressions.append(expr.expression)

        return list_of_expressions

    def add_gen(self, node_id: str, expr_str: str) -> None:
        '''
        Add GEN record for a node
        '''
        if node_id not in self.GEN:
            self.GEN[node_id] = set()

        self.GEN[node_id].add(expr_str)

    def add_kill(self, node_id: str, expr_str: str) -> None:
        '''
        Add KILL record for a node
        '''
        if node_id not in self.KILL:
            self.KILL[node_id] = set()

        self.KILL[node_id].add(expr_str)

    def compute(self) -> None:
        '''
        Compute the available expression data flow analysis
        '''

        self.__compute_expressions()
        print(self.expr_table.keys())

        self.__compute_gen_kill()
        print(self.GEN)
        print(self.KILL)

    def __compute_expressions(self) -> None:
        '''
        Compute and enroll all the expressions present in the CFG
        '''

        visited = set()

        def traverse(node_id, visited: set, cfg: ControlFlowGraph):
            '''
            Traverse the Graph and Compute the GEN and KILL functions
            '''

            if node_id in visited:
                return

            # add to visited set
            visited.add(node_id)

            # get node instance / object
            node = cfg.cfg_metadata.get_node(node_id)

            expr = None
            if node.node_type == 'VariableDeclarationStatement':
                expr = build_variable_declaration(node)
            if node.node_type == 'ExpressionStatement':
                expr = build_expression(node)

            # register the expressions
            if expr is not None:
                self.set_node_expr(node_id, expr)
                if len(expr.right_symbols) > 0:
                    self.set_expr(expr.right_str, expr.right_symbols)

            print("EXPR-SEARCH", node_id)

            if node_id != self.ending_node:
                for child_id in node.next_nodes:
                    child_node = cfg.cfg_metadata.get_node(child_id)

                    traverse(child_node.cfg_id, visited, cfg)

        traverse(self.starting_node, visited, self.cfg)

    def __compute_gen_kill(self) -> None:
        '''
        Compute the GEN and KILL functions for all the nodes
        '''

        visited = set()

        def traverse(node_id, visited: set, cfg: ControlFlowGraph):
            '''
            Traverse the Graph and Compute the GEN and KILL functions
            '''

            if node_id in visited:
                return

            # add to visited set
            visited.add(node_id)

            # get node instance / object
            node = cfg.cfg_metadata.get_node(node_id)

            expr = None
            if node.node_type == 'VariableDeclarationStatement' or node.node_type == 'ExpressionStatement':
                expr = self.get_node_expr(node_id)

            ###########################
            # compute the generates set
            # if there are right symbols present, and no right symbol is present in the left side
            # if a symbol from the right side is present in the left side, this means, it is writing after generation
            # in that case the generated set will be empty
            if expr is not None:
                if len(expr.right_symbols) > 0 and len(expr.right_symbols.intersection(expr.left_symbols)) == 0:
                    self.add_gen(node_id, expr.right_str)

            ###########################
            # compute the kills set
            if expr is not None:
                for symbol in expr.left_symbols:
                    for expression in self.get_exprs_with_symbol(symbol):
                        self.add_kill(node_id, expression)

            print("GEN-KILL", node_id)

            if node_id != self.ending_node:
                for child_id in node.next_nodes:
                    child_node = cfg.cfg_metadata.get_node(child_id)

                    traverse(child_node.cfg_id, visited, cfg)

        traverse(self.starting_node, visited, self.cfg)
