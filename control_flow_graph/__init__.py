from graphviz import Digraph

from control_flow_graph.node_processor import CFGMetadata
import control_flow_graph.node_processor.nodes as nodes
from control_flow_graph.node_processor import Node, ExtraNodes
from control_flow_graph.node_processor.nodes.extra_nodes.SourceEntry import SourceEntry
from control_flow_graph.node_processor.nodes.extra_nodes.SourceExit import SourceExit


class ControlFlowGraph(object):
    '''
    The CFG Wrapper class, 
    encapsulating the complete functionality of building 
    and traversing the CFG from AST. 
    '''

    def __init__(self, source: str, ast: dict) -> None:
        self.source_code = source
        self.ast = ast

        # init graph
        self.graph = Digraph(comment='Control Flow Graph')

        # initialize the metadata handler
        self.cfg_metadata = CFGMetadata()

        # generate the entry and exit nodes
        self.entry_node = SourceEntry(dict(), None, None,
                                      None, self.cfg_metadata)

        self.exit_node = SourceExit(dict(), None, None,
                                    None, self.cfg_metadata)

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
        child_node = nodeConstructor(self.ast, self.entry_node.cfg_id, self.entry_node.cfg_id,
                                     self.exit_node.cfg_id, self.cfg_metadata)

        # add the ast's first node's ID to the next_nodes list of the entry node
        self.entry_node.add_next_node(child_node.cfg_id)

        leaves = child_node.get_leaf_nodes()

        for leaf in leaves:
            node = self.cfg_metadata.get_node(leaf)
            node.add_prev_node(self.exit_node.cfg_id)

            self.exit_node.add_prev_node(leaf)

    def generate_dot(self) -> str:
        '''
        Traverse the CFG and generate a Graphviz Digraph DOT file
        '''
        graph = Digraph(comment='Abstract Syntax Tree')
        visited = set()

        def traverse(node_id, graph: Digraph, visited: set, cfg_metadata: CFGMetadata):
            '''
            Traverse the Graph and Generate the Digraph
            '''

            if node_id in visited:
                return

            # add to visited set
            visited.add(node_id)

            # get node instance / object
            node = cfg_metadata.get_node(node_id)

            print(node_id)

            graph.node(node_id, label=node.node_type)

            print(
                getattr(node, 'next_nodes', None),
                getattr(node, 'previous_nodes', None))

            for child in node.next_nodes:
                child_node = cfg_metadata.get_node(child)

                traverse(child_node.cfg_id, graph, visited, cfg_metadata)

                graph.edge(node_id, child)

            if len(node.next_nodes) == 0:
                graph.edge(node_id, 'ExtraNodes.EX_SOURCE_0')

        traverse(self.entry_node.cfg_id, graph, visited, self.cfg_metadata)

        graph.render(filename='./gen/cfg.png')
