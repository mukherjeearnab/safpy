'''
Class definition for the Function Definition CFG (AST) node
'''
from graphviz import Digraph
from control_flow_graph.helpers import CFGMetadata
from control_flow_graph.node_processor.nodes import Node, BasicBlockTypes, ExtraNodes
import control_flow_graph.node_processor.nodes as nodes


class FunctionDefinition(Node):
    '''
    Function Definition Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata, graph: Digraph):
        '''
        Constructor
        '''
        super(FunctionDefinition, self).__init__(ast_node, entry_node_id, prev_node_id,
                                                 join_node_id, exit_node_id,
                                                 cfg_metadata, graph)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.FunctionBody
        self.node_type = 'FunctionDefinition'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # allocate this node to the graph and
        # add an edge from the previous node to this one
        graph.node(self.cfg_id, label=self.cfg_id)
        graph.edge(prev_node_id, self.cfg_id)

        # node specific metadata
        self.documentation = ast_node.get('documentation', None)
        self.implemented = ast_node.get('implemented', None)
        self.isConstructor = ast_node.get('isConstructor', None)
        self.isDeclaredConst = ast_node.get('isDeclaredConst', None)
        self.modifiers = ast_node.get('modifiers', list())
        self.parameters = ast_node.get('parameters', dict())
        self.returnParameters = ast_node.get('returnParameters', dict())
        self.payable = ast_node.get('payable', None)
        self.stateMutability = ast_node.get('stateMutability', None)
        self.superFunciton = ast_node.get('superFunction', None)
        self.visibility = ast_node.get('visibility', None)
        self.name = ast_node.get('name', None)
        self.scope = ast_node.get('scope', None)

        # create the function entry node and
        # add the node to the next_nodes list
        # also add an edge from this node to the entry node
        function_entry = Node(dict(), self.entry_node, self.cfg_id,
                              self.join_node, None,
                              cfg_metadata, graph, extra_node=ExtraNodes.EN_FN)
        self.next_nodes.add(function_entry.cfg_id)
        graph.edge(self.cfg_id, function_entry.cfg_id)

        # create the exit node for the function and
        # link the exit function to the exit of the source unit
        function_exit = Node(dict(), function_entry.cfg_id, self.cfg_id,
                             self.join_node, self.exit_node,
                             cfg_metadata, graph, extra_node=ExtraNodes.EX_FN)

        # perform logic to create the body of the function
        body_statements = ast_node['body']['statements']
        body_prev_statement = function_entry.cfg_id
        for statement in body_statements:
            # obtain the child node's type
            child_node_type = statement['nodeType']

            # obtain the child node's constructor
            childConstructor = getattr(nodes, child_node_type, Node)

            # initialize the child node (recursive)
            child_node = childConstructor(statement,
                                          function_entry.cfg_id, body_prev_statement,
                                          self.join_node, function_exit.cfg_id,
                                          cfg_metadata, graph)

            # add the child node's ID to the next_nodes list
            body_prev_statement = child_node.cfg_id

        # set the previous node of the exit node as the last statement of the body
        # also add the edge to the previous statement to the exit node
        function_exit.add_prev_node(body_prev_statement)
        graph.edge(body_prev_statement, function_exit.cfg_id)
