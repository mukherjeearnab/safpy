'''
Class definition for the Function Definition CFG (AST) node
'''
from graphviz import Digraph
from control_flow_graph.node_processor import CFGMetadata
from control_flow_graph.node_processor import Node, BasicBlockTypes, ExtraNodes
import control_flow_graph.node_processor.nodes as nodes
from control_flow_graph.node_processor.nodes.extra_nodes.FunctionEntry import FunctionEntry
from control_flow_graph.node_processor.nodes.extra_nodes.FunctionExit import FunctionExit


class FunctionDefinition(Node):
    '''
    Function Definition Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 exit_node_id: str, cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''
        super(FunctionDefinition, self).__init__(ast_node, entry_node_id, prev_node_id,
                                                 exit_node_id, cfg_metadata)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.FunctionBody
        self.node_type = 'FunctionDefinition'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

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
        function_entry = FunctionEntry(dict(), self.entry_node, self.cfg_id,
                                       None, cfg_metadata)
        self.add_next_node(function_entry.cfg_id)

        # create the exit node for the function and
        # link the exit function to the exit of the source unit
        function_exit = FunctionExit(dict(), function_entry.cfg_id, None,
                                     self.exit_node, cfg_metadata)

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
                                          function_exit.cfg_id, cfg_metadata)

            # add the child node's ID to the next_nodes list
            body_prev_statement = child_node.cfg_id

        # set the previous node of the exit node as the last statement of the body
        function_exit.add_prev_node(body_prev_statement)

        self.leaves.add(function_exit.cfg_id)

    def get_leaf_nodes(self) -> set:
        '''
        Returns the leaf node(a) in the current branch,
        where the current node is the root node 
        '''

        return self.leaves
