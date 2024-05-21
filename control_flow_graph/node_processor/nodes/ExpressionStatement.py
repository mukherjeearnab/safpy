'''
Class definition for the Expression Statement CFG (AST) node
'''
from graphviz import Digraph
from control_flow_graph.node_processor import CFGMetadata
from control_flow_graph.node_processor import BasicBlockTypes
from control_flow_graph.node_processor import Node


class ExpressionStatement(Node):
    '''
    Expression Statement Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 exit_node_id: str, cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''
        super(ExpressionStatement, self).__init__(ast_node, entry_node_id, prev_node_id,
                                                  exit_node_id, cfg_metadata)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Statement
        self.node_type = 'ExpressionStatement'

        # link the previous node to indexing
        self.add_prev_node(prev_node_id)

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # node specific metadata
        # exported symbols from the source unit
        self.expresion = ast_node.get('expresion', dict())

        self.leaves.add(self.cfg_id)

    def get_leaf_nodes(self) -> set:
        '''
        Returns the leaf node(a) in the current branch,
        where the current node is the root node 
        '''
        child_leaves = set()
        # recursively traverse all the nodes till we hit the leaf nodes
        for node_id in self.next_nodes.keys():
            node = self.cfg_metadata.get_node(node_id)
            _leaves = node.get_leaf_nodes()

            child_leaves.update(_leaves)

        if len(child_leaves) > 0:
            self.leaves = set()
            self.leaves.update(child_leaves)

        return self.leaves
