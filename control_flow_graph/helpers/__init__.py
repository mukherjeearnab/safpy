from enum import Enum
from typing import Union
from collections import defaultdict
from graphviz import Digraph


class BasicBlockTypes(Enum):
    '''
    Basic Block Types Enum Definition
    '''
    Entry = 'Entry_Block'
    Exit = 'Exit_Block'

    Statement = 'Statement_Block'
    FunctionBody = 'FunctionBody_Block'
    ClassBody = 'ClassBody_Block'

    Conditional = 'Conditional_Block'
    Loop = 'LoopBlock'
    Branch = 'Branch_Block'

    FunctionCall = 'FunctionCall_Block'


class ExtraNodes(Enum):
    CN_F = 'ForLoop_Condition'
    CN_W = 'WhileLoop_Condition'
    CN_DW = 'DoWhileLoop_Condition'

    JN_F = 'ForLoop_Join'
    JN_W = 'WhileLoop_Join'
    JN_DW = 'DoWhileLoop_Join'
    JN_IF = 'IfCOndition_Join'

    EN_SOURCE = 'SourceUnit_Entry'
    EN_DW = 'DoWhileLoop_Entry'
    EN_FN = 'FunctionBody_Entry'

    EX_FN = 'FunctionBody_Exit'
    EX_SOURCE = 'SourceUnit_Exit'


class Node(object):
    '''
    Base class for nodes
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata, graph: Digraph, extra_node=None):
        '''
        Constructor
        '''

        _ = cfg_metadata

        # set the basic block type and node type
        if not extra_node is None:
            self.basic_block_type = \
                BasicBlockTypes.Entry if 'Entry' in extra_node.value else BasicBlockTypes.Exit
            self.node_type = extra_node.value
            self.cfg_id = cfg_metadata.register_node(self, extra_node)

            print(f'Processing CFG Node {self.cfg_id}')

            # allocate this node to the graph and
            # add an edge from the previous node to this one
            graph.node(self.cfg_id, label=self.cfg_id)
            if prev_node_id is not None:
                graph.edge(prev_node_id, self.cfg_id)

        # set the entry node and the exit node
        # entry node is start (global) and exit node is end (global)
        self.entry_node = entry_node_id
        self.exit_node = exit_node_id

        # init next nodes as a list of node ids
        # same goes for previous nodes, but we initially add the previous_node
        # here previous node is the one from which we call this node's constructor
        self.next_nodes = set()
        self.previous_nodes = set()
        if not prev_node_id is None:
            self.previous_nodes.add(prev_node_id)

        # also, if a join node is being supplied, apply it
        # this is somewhat similar to how the exit node is propagated
        self.join_node = join_node_id

        if extra_node is None:
            # set the source map in the form (s:l:i)
            # s = start index, l = length, i = index
            self.src_map = (int(i) for i in ast_node['src'].split(':')) \
                if 'src' in ast_node else None

            # set the ast id, if available
            self.ast_id = ast_node.get('id', None)

            # set the children nodes from the AST node information
            self.children = ast_node.get('nodes', list())

    def add_prev_node(self, node_id: str) -> None:
        '''
        Method to add previous node's id
        '''

        self.previous_nodes.add(node_id)

    def add_next_node(self, node_id: str) -> None:
        '''
        Method to add next node's id
        '''

        self.next_nodes.add(node_id)

    def set_entry_node(self, node_id: str) -> None:
        '''
        Set node id of the entry node
        '''

        self.entry_node = node_id

    def set_exit_node(self, node_id: str) -> None:
        '''
        Set node id of the exit node
        '''

        self.exit_node = node_id


class CFGMetadata(object):
    '''
    Metadata Container Class Definition
    '''

    def __init__(self):
        # this contains the mapping of Node ID to node object
        self.node_table = dict()

        # this contains the mapping of node type to
        # the count of that type of nodes
        self.node_count = defaultdict(int)

    def register_node(self, node_pointer: Node, node_type: str) -> str:
        '''
        Register and Return the Node's Given ID
        '''

        # generate the node id (starts from 0)
        node_id = f'{node_type}_{self.node_count[node_type]}'

        # and increment the node type count
        self.node_count[node_type] += 1

        # add the node object to the mapping table
        self.node_table[node_id] = node_pointer

        # return the node id
        return node_id

    def get_node(self, node_id: str) -> Union[Node, None]:
        '''
        Get the Node object from the node ID
        '''

        return self.node_table.get(node_id, None)
