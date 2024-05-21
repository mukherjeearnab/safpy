'''
Class definition for the If Statement CFG (AST) node
'''
from graphviz import Digraph
from control_flow_graph.node_processor import CFGMetadata
from control_flow_graph.node_processor import Node, ExtraNodes, BasicBlockTypes
import control_flow_graph.node_processor.nodes as nodes
from control_flow_graph.node_processor.nodes.extra_nodes.IfConditionJoin import IfConditionJoin


class IfStatement(Node):
    '''
    If Statement Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 exit_node_id: str, cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''
        super(IfStatement, self).__init__(ast_node, entry_node_id, prev_node_id,
                                          exit_node_id, cfg_metadata)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Conditional
        self.node_type = 'IfStatement'

        # link the previous node to indexing
        self.add_prev_node(prev_node_id)

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # node specific metadata
        self.condition = ast_node.get('condition', dict())

        # generate the join node
        join_node = IfConditionJoin(dict(), self.entry_node, None,
                                    self.exit_node, cfg_metadata)
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
                                          self.join_node, cfg_metadata)

            # obtain the cfg_id for the next node for the if block
            if i == 0:
                self.add_next_node(child_node.cfg_id, label='True')
                self.true_body_next = child_node.cfg_id
            else:
                # also link the previous statement in the block with the current statement
                # 1. first obtain the prev node's leaves
                child_leaves = self.cfg_metadata.get_node(
                    body_prev_statement).get_leaf_nodes()

                # 2. now check if the leaf node is there or we need to link the previous node itself
                to_link = body_prev_statement if len(
                    child_leaves) == 0 else child_leaves.pop()

                # 3. link the leaf node's next as the child node
                self.cfg_metadata.get_node(
                    to_link).add_next_node(child_node.cfg_id)

            # add the child node's ID to the next_nodes list
            body_prev_statement = child_node.cfg_id

            if i == len(true_body_statements) - 1:
                self.leaves.update(child_node.get_leaf_nodes())

        # # add the join node's previous node as the last child of the block
        # join_node.add_prev_node(body_prev_statement)

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
                                          self.join_node, cfg_metadata)

            # obtain the cfg_id for the next node for the if block
            if i == 0:
                self.add_next_node(child_node.cfg_id, label='False')
                self.false_body_next = child_node.cfg_id
            else:
                # also link the previous statement in the block with the current statement
                # 1. first obtain the prev node's leaves
                child_leaves = self.cfg_metadata.get_node(
                    body_prev_statement).get_leaf_nodes()

                # 2. now check if the leaf node is there or we need to link the previous node itself
                to_link = body_prev_statement if len(
                    child_leaves) == 0 else child_leaves.pop()

                # 3. link the leaf node's next as the child node
                self.cfg_metadata.get_node(
                    to_link).add_next_node(child_node.cfg_id)

            # add the child node's ID to the next_nodes list
            body_prev_statement = child_node.cfg_id

            if i == len(false_body_statements) - 1:
                self.leaves.update(child_node.get_leaf_nodes())

        while len(self.leaves) != 0:
            print("IFLEAF", self.leaves)
            last_stmt_node = self.leaves.pop()

            # add the join node's previous node as the last child of the block
            join_node.add_prev_node(last_stmt_node)

            # also add the next node of last child as the exit node
            cfg_metadata.get_node(
                last_stmt_node).add_next_node(self.join_node)

        # finally add the join node as the leaf
        self.leaves.add(self.join_node)

    def get_leaf_nodes(self) -> set:
        '''
        Returns the leaf node(a) in the current branch,
        where the current node is the root node 
        '''
        child_leaves = set()

        # obtain the join_node
        join_node = self.cfg_metadata.get_node(self.join_node)

        # recursively traverse all the nodes till we hit the leaf nodes
        for node_id in join_node.next_nodes.keys():
            node = self.cfg_metadata.get_node(node_id)
            _leaves = node.get_leaf_nodes()

            child_leaves.update(_leaves)

        if len(child_leaves) > 0:
            self.leaves = set()
            self.leaves.update(child_leaves)

        return self.leaves
