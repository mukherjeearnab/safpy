'''
Class definition for the Source Unit CFG (AST) node
'''
from graphviz import Digraph
from control_flow_graph.helpers import CFGMetadata
from control_flow_graph.node_processor.nodes import BasicBlockTypes
from control_flow_graph.node_processor.nodes import Node
import control_flow_graph.node_processor.nodes as nodes


class SourceUnit(Node):
    '''
    Source Unit Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata, graph: Digraph):
        '''
        Constructor
        '''
        super(SourceUnit, self).__init__(ast_node, entry_node_id, prev_node_id,
                                         join_node_id, exit_node_id,
                                         cfg_metadata, graph)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Entry
        self.node_type = 'SourceUnit'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # allocate this node to the graph and
        # add an edge from the previous node to this one
        graph.node(self.cfg_id, label=self.cfg_id)
        graph.edge(prev_node_id, self.cfg_id)

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
            child_node = childConstructor(child, self.entry_node, self.cfg_id,
                                          self.join_node, self.exit_node,
                                          cfg_metadata, graph)

            # add the child node's ID to the next_nodes list
            self.next_nodes.add(child_node.cfg_id)
