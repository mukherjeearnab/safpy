'''
Class definition for the Source Unit CFG (AST) node
'''
from typing import Union
from control_flow_graph.node_processor import CFGMetadata
from control_flow_graph.node_processor import BasicBlockTypes
from control_flow_graph.node_processor.nodes import Node
import control_flow_graph.node_processor.nodes as nodes


class SourceUnit(Node):
    '''
    Source Unit Node
    '''

    def __init__(self, ast_node: Union[dict, str],
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''
        super(SourceUnit, self).__init__(ast_node, entry_node_id, prev_node_id,
                                         join_node_id, exit_node_id,
                                         cfg_metadata)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.EntryBlock
        self.node_type = 'SourceUnit'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        # node specific metadata
        # exported symbols from the source unit
        self.exported_symbols = ast_node.get('exportedSymbols', dict())

        # traverse the children and construct the rest of the CFG recursively
        for child in self.children:
            # obtain the child node's type
            child_node_type = child['nodeType']

            # obtain the child node's constructor
            childConstructor = getattr(nodes, child_node_type)

            # initialize the child node (recursive)
            child_node = childConstructor(self.entry_node, self.cfg_id,
                                          self.join_node, self.exit_node,
                                          cfg_metadata)

            # add the child node's ID to the next_nodes list
            self.next_nodes.append(child_node.cfg_id)
