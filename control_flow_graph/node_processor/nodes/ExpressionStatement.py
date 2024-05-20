'''
Class definition for the Expression Statement CFG (AST) node
'''
from control_flow_graph.helpers import CFGMetadata
from control_flow_graph.node_processor.nodes import BasicBlockTypes
from control_flow_graph.node_processor.nodes import Node


class ExpressionStatement(Node):
    '''
    Expression Statement Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''
        super(ExpressionStatement, self).__init__(ast_node, entry_node_id, prev_node_id,
                                                  join_node_id, exit_node_id,
                                                  cfg_metadata)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Statement
        self.node_type = 'ExpressionStatement'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # node specific metadata
        # exported symbols from the source unit
        self.expresion = ast_node.get('expresion', dict())
