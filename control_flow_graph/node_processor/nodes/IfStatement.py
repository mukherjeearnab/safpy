'''
Class definition for the If Statement CFG (AST) node
'''
from graphviz import Digraph
from control_flow_graph.helpers import CFGMetadata
from control_flow_graph.node_processor.nodes import Node, ExtraNodes, BasicBlockTypes
import control_flow_graph.node_processor.nodes as nodes


class IfStatement(Node):
    '''
    If Statement Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata, graph: Digraph):
        '''
        Constructor
        '''
        super(IfStatement, self).__init__(ast_node, entry_node_id, prev_node_id,
                                          join_node_id, exit_node_id,
                                          cfg_metadata, graph)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Conditional
        self.node_type = 'IfStatement'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # allocate this node to the graph and
        # add an edge from the previous node to this one
        graph.node(self.cfg_id, label=self.cfg_id)
        graph.edge(prev_node_id, self.cfg_id)

        # node specific metadata
        self.condition = ast_node.get('condition', dict())

        # generate the join node
        join_node = Node(dict(), self.entry_node, None,
                         None, self.exit_node,
                         cfg_metadata, graph, extra_node=ExtraNodes.JN_IF)
        self.join_node = join_node.cfg_id

        ######################
        # True Body Processing
        # first generate the true body of the conditional (recursively)
        true_body_statements = ast_node['trueBody']['statements']
        body_prev_statement = self.cfg_id
        for i, statement in enumerate(true_body_statements):
            # obtain the child node's type
            child_node_type = statement['nodeType']

            # obtain the child node's constructor
            childConstructor = getattr(nodes, child_node_type, Node)

            # initialize the child node (recursive)
            child_node = childConstructor(statement,
                                          self.entry_node, body_prev_statement,
                                          self.join_node, self.cfg_id,
                                          cfg_metadata, graph)

            # add the child node's ID to the next_nodes list
            body_prev_statement = child_node.cfg_id

            # obtain the cfg_id for the next node for the if block
            if i == 0:
                self.add_next_node(child_node.cfg_id)
                self.true_body_next = child_node.cfg_id

                # also add the true edge from the conditional
                graph.edge(self.cfg_id, child_node.cfg_id, label="True")

        # add the join node's previous node as the last child of the block
        # and link with the join node in the graph
        join_node.add_prev_node(body_prev_statement)
        graph.edge(body_prev_statement, self.join_node)

        # also add the next node of last child as the join node
        cfg_metadata.get_node(
            body_prev_statement).add_next_node(self.join_node)

        #######################
        # False Body Processing
        # now we generate the false body of the conditional (recursively)
        false_body_statements = ast_node['falseBody']['statements']
        body_prev_statement = self.cfg_id
        for i, statement in enumerate(false_body_statements):
            # obtain the child node's type
            child_node_type = statement['nodeType']

            # obtain the child node's constructor
            childConstructor = getattr(nodes, child_node_type, Node)

            # initialize the child node (recursive)
            child_node = childConstructor(statement,
                                          self.entry_node, body_prev_statement,
                                          self.join_node, self.cfg_id,
                                          cfg_metadata, graph)

            # add the child node's ID to the next_nodes list
            body_prev_statement = child_node.cfg_id

            # obtain the cfg_id for the next node for the if block
            if i == 0:
                self.add_next_node(child_node.cfg_id)
                self.false_body_next = child_node.cfg_id

                # also add the true edge from the conditional
                graph.edge(self.cfg_id, child_node.cfg_id, label="False")

        # add the join node's previous node as the last child of the block
        # and link with the join node in the graph
        join_node.add_prev_node(body_prev_statement)
        graph.edge(body_prev_statement, self.join_node)

        # also add the next node of last child as the join node
        cfg_metadata.get_node(
            body_prev_statement).add_next_node(self.join_node)
