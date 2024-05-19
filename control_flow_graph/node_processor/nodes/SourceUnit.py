'''
Class definition for the Pragma Directive CFG (AST) node
'''
from typing import Union
from control_flow_graph.node_processor import CFGMetadata
from control_flow_graph.node_processor.nodes import BasicBlockTypes
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

        self.basic_block_type = BasicBlockTypes.EntryBlock
        self.node_type = 'SourceUnit'

        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        self.entry_node = entry_node_id
        self.exit_node = exit_node_id

        self.next_nodes = []
        self.previous_nodes = [prev_node_id]

        self.join_node = join_node_id

        self.src_map = (int(i) for i in ast_node['src'].split(':'))
        self.ast_id = ast_node['id']
        self.children = ast_node['nodes']

        for child in self.children:
            child_node_type = child['nodeType']

            childConstructor = getattr(nodes, child_node_type)
            child_node = childConstructor(self.entry_node, self.cfg_id,
                                          self.join_node, self.exit_node,
                                          cfg_metadata)

            self.next_nodes.append(child_node.cfg_id)
