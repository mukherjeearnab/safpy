'''
Class definition for the Pragma Directive CFG (AST) node
'''
from graphviz import Digraph
from control_flow_graph.helpers import CFGMetadata
from control_flow_graph.node_processor.nodes import BasicBlockTypes
from control_flow_graph.node_processor.nodes import Node


class PragmaDirective(Node):
    '''
    PragmaDirective Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata, graph: Digraph):
        '''
        Constructor
        '''
        super(PragmaDirective, self).__init__(ast_node, entry_node_id, prev_node_id,
                                              join_node_id, exit_node_id,
                                              cfg_metadata, graph)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Statement
        self.node_type = 'PragmaDirective'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # allocate this node to the graph and
        # add an edge from the previous node to this one
        graph.node(self.cfg_id, label=self.cfg_id)
        graph.edge(prev_node_id, self.cfg_id)

        # node specific metadata
        # obtain the literals of the pragma directive
        self.literals = ast_node.get('literals', list())

        # add the exit node to the next node and end it
        self.next_nodes.add(exit_node_id)

        # also add the link to the source exit node
        graph.edge(self.cfg_id, exit_node_id)
