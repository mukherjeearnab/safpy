from control_flow_graph.helpers import CFGMetadata
import control_flow_graph.node_processor.nodes as nodes
from control_flow_graph.node_processor.nodes import Node, ExtraNodes


class ControlFlowGraph(object):
    '''
    The CFG Wrapper class, 
    encapsulating the complete functionality of building 
    and traversing the CFG from AST. 
    '''

    def __init__(self, source: str, ast: dict) -> None:
        self.source_code = source
        self.ast = ast

        # initialize the metadata handler
        self.cfg_metadata = CFGMetadata()

        # generate the entry and exit nodes
        self.entry_node = Node(dict(), None, None,
                               None, None,
                               self.cfg_metadata, extra_node=ExtraNodes.EN_SOURCE)

        self.exit_node = Node(dict(), None, None,
                              None, None,
                              self.cfg_metadata, extra_node=ExtraNodes.EX_SOURCE)

        # link the entry and exit nodes
        self.entry_node.set_entry_node(self.entry_node.cfg_id)
        self.entry_node.set_exit_node(self.exit_node.cfg_id)
        self.exit_node.set_entry_node(self.entry_node.cfg_id)
        self.exit_node.set_exit_node(self.exit_node.cfg_id)

    def build_cfg(self) -> None:
        '''
        Build the CFG recursively
        '''

        # obtain the AST's first node's type
        node_type = self.ast['nodeType']

        # obtain the child node's constructor
        nodeConstructor = getattr(nodes, node_type)

        # initialize the child node (recursive)
        child_node = nodeConstructor(self.ast, self.entry_node, self.entry_node,
                                     None, self.exit_node,
                                     self.cfg_metadata)

        # add the ast's first node's ID to the next_nodes list of the entry node
        self.entry_node.next_nodes.add(child_node.cfg_id)
