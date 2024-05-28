'''
Class definition for the ForStatement CFG (AST) node
'''
from control_flow_graph.node_processor import CFGMetadata
from control_flow_graph.node_processor import Node, BasicBlockTypes
import control_flow_graph.node_processor.nodes as nodes
from control_flow_graph.node_processor.nodes.extra_nodes.for_loop.join import ForLoopJoin
from control_flow_graph.node_processor.nodes.extra_nodes.for_loop.continuee import ForLoopContinue


class ForStatement(Node):
    '''
    ForStatement Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 exit_node_id: str, cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''
        super(ForStatement, self).__init__(ast_node, entry_node_id, prev_node_id,
                                           exit_node_id, cfg_metadata)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Loop
        self.node_type = 'ForStatement'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # node specific metadata
        self.condition = ast_node.get('condition', dict())

        ############################
        # Set Continue Node
        # generate the continue node
        continue_node = ForLoopContinue(dict(), self.entry_node, None,
                                        self.exit_node, cfg_metadata)

        # link the next node of the continue node
        self.continue_node = continue_node.cfg_id
        self.add_prev_node(self.continue_node)
        continue_node.add_next_node(self.cfg_id, _internal=True)

        ############################
        # Set Initializer Node
        # generate the initilization node
        init_node_ast = ast_node.get('initializationExpression', dict())

        # obtain the init node's type
        init_node_type = init_node_ast['nodeType']

        # obtain the child node's constructor
        initConstructor = getattr(nodes, init_node_type, Node)

        # initialize the child node (recursive)
        init_node = initConstructor(init_node_ast, self.entry_node, prev_node_id,
                                    self.exit_node, self.cfg_metadata)

        # set and link the init node
        self.init_node = init_node.cfg_id
        init_node.add_next_node(self.continue_node)
        continue_node.add_prev_node(self.init_node)

        ############################
        # Set Join Node
        # generate the join node
        join_node = ForLoopJoin(dict(), self.entry_node, self.cfg_id,
                                self.exit_node, cfg_metadata)
        self.join_node = join_node.cfg_id

        # link the join node to the current node as the break edge
        self.add_next_node(self.join_node, label='break')
        join_node.add_prev_node(self.cfg_id, label='break')

        ######################
        # Body Processing
        # first generate the body of the loop (recursively)
        body_statements = ast_node['body']['statements']
        body_prev_statement = self.cfg_id
        for i, statement in enumerate(body_statements):
            # obtain the child node's type
            child_node_type = statement['nodeType']

            # obtain the child node's constructor
            childConstructor = getattr(nodes, child_node_type, Node)

            # initialize the child node (recursive)
            child_node = childConstructor(statement,
                                          self.entry_node, body_prev_statement,
                                          self.continue_node, cfg_metadata)

            # for the first statement node in the block, link it to the while condition
            # and label the edge as the Body (true)
            if i == 0:
                self.add_next_node(child_node.cfg_id)
                self.body_next = child_node.cfg_id
            else:
                # in case of the statement is not first,
                # link the previous statement in the block with the current statement
                # 1. first obtain the prev node's leaves
                prev_leaves = self.cfg_metadata.get_node(
                    body_prev_statement).get_leaf_nodes()

                # 2. now check if a leaf node is there or we need to link the previous node itself
                to_link = body_prev_statement if len(
                    prev_leaves) == 0 else next(iter(prev_leaves))

                print("TOLINK", body_prev_statement, to_link, prev_leaves)

                # 3. link the leaf node's next as the current child node
                self.cfg_metadata.get_node(
                    to_link).add_next_node(child_node.cfg_id)

            # add the child node's ID as the previous statement for next iteration
            body_prev_statement = child_node.cfg_id if child_node.join_node is None else child_node.join_node

        ############################
        # Set Loop Expression Node
        # generate the loop expression node
        loop_node_ast = ast_node.get('loopExpression', dict())

        # obtain the loop node's type
        loop_node_type = loop_node_ast['nodeType']

        # obtain the child node's constructor
        loopConstructor = getattr(nodes, loop_node_type, Node)

        # initialize the child node (recursive)
        loop_node = loopConstructor(loop_node_ast, self.entry_node, None,
                                    self.exit_node, self.cfg_metadata)

        # set and link the loop node with the last child node of the loop body statements
        self.loop_node = loop_node.cfg_id
        self.cfg_metadata.get_node(
            body_prev_statement).add_next_node(self.loop_node)
        loop_node.add_prev_node(body_prev_statement)

        # for the loop expr node being the last node in the block,
        # connect it to the continue node
        loop_node.add_next_node(self.continue_node)
        continue_node.add_prev_node(self.loop_node)

        # finally add the join node as the leaf
        # (at this point the leaf nodes set should be empty)
        self.leaves.add(self.join_node)

    def get_leaf_nodes(self) -> set:
        '''
        Returns the leaf node(a) in the current branch,
        where the current node is the root node 

        Note that this might not have children, but this can be part of a Block statemtent,
        hence a chain of statements, therefore we check the next nodes for leaf nodes.

        However unlike simple statements, this time we start with the next nodes of the join node
        '''

        # init child leaves
        child_leaves = set()

        # obtain the join_node
        join_node = self.cfg_metadata.get_node(self.join_node)

        # recursively traverse all the nodes of the join node till we hit the leaf nodes
        for node_id in join_node.next_nodes.keys():
            # obtain the next node's instance
            node = self.cfg_metadata.get_node(node_id)

            # obtain their leaf nodes (recursive)
            _leaves = node.get_leaf_nodes()

            # add them to the child nodes
            child_leaves.update(_leaves)

        # now if there are leaf nodes obtained from the next node,
        # we need to drop the leaf nodes of the current node
        # and propogate the nodes of the next node as leaf nodes
        if len(child_leaves) > 0:
            # reset leaves
            self.leaves = set()

            # add the child nodes
            self.leaves.update(child_leaves)

        return self.leaves

    def get_whois_next_node(self) -> str:
        '''
        Get who is the next node for their node id
        For nodes like for or while loops,
        nodes like the continue and initialiation statement become the next node, 
        instead of the loop statement / condition node.

        This method handles such special cases where the next node might not exactly be the node itself, 
        but rather some special node of that node's block

        In this case we return the id of the initlization node of the for loop
        '''
        return self.init_node