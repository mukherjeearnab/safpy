'''
Class definition for the Pragma Directive CFG (AST) node
'''

from typing import Union
from control_flow_graph.node_processor import CFGMetadata
from control_flow_graph.node_processor import BasicBlockTypes
from control_flow_graph.node_processor.nodes import Node
import control_flow_graph.node_processor.nodes as nodes


class PragmaDirective(Node):
    '''
    PragmaDirective Node
    '''

    def __init__(self, ast_node: Union[dict, str],
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''
        super(PragmaDirective, self).__init__(ast_node, entry_node_id, prev_node_id,
                                              join_node_id, exit_node_id,
                                              cfg_metadata)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Statement
        self.node_type = 'PragmaDirective'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        # node specific metadata
        # obtain the literals of the pragma directive
        self.literals = ast_node.get('literals', list())

        # add the exit node to the next node and end it
        self.next_nodes.append(exit_node_id)
