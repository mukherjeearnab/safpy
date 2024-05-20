'''
Class definition for the Variable Declaration CFG (AST) node
'''
from control_flow_graph.helpers import CFGMetadata
from control_flow_graph.node_processor.nodes import BasicBlockTypes
from control_flow_graph.node_processor.nodes import Node
import control_flow_graph.node_processor.nodes as nodes


class VariableDeclaration(Node):
    '''
    Variable Declaration Node
    '''

    def __init__(self, ast_node: dict,
                 entry_node_id: str, prev_node_id: str,
                 join_node_id: str, exit_node_id: str,
                 cfg_metadata: CFGMetadata):
        '''
        Constructor
        '''
        super(VariableDeclaration, self).__init__(ast_node, entry_node_id, prev_node_id,
                                                  join_node_id, exit_node_id,
                                                  cfg_metadata)

        # set the basic block type and node type
        self.basic_block_type = BasicBlockTypes.Statement
        self.node_type = 'VariableDeclaration'

        # register the node to the CFG Metadata store and
        # obtain a CFG ID of the form f'{node_type}_{n}'
        self.cfg_id = cfg_metadata.register_node(self, self.node_type)

        print(f'Processing CFG Node {self.cfg_id}')

        # node specific metadata
        self.constant = ast_node.get('constant', None)
        self.visibility = ast_node.get('visibility', None)
        self.value = ast_node.get('value', dict())
        self.typeName = ast_node.get('typeName', dict())
        self.typeDescriptions = ast_node.get('typeDescriptions', dict())
        self.storageLocation = ast_node.get('storageLocation', None)
        self.stateVariable = ast_node.get('stateVariable', None)
        self.name = ast_node.get('name', None)
        self.scope = ast_node.get('scope', None)

        # traverse the children and construct the rest of the CFG recursively
        for child in self.children:
            # obtain the child node's type
            child_node_type = child['nodeType']

            # obtain the child node's constructor
            childConstructor = getattr(nodes, child_node_type)

            # initialize the child node (recursive)
            child_node = childConstructor(child, self.entry_node, self.cfg_id,
                                          self.join_node, self.exit_node,
                                          cfg_metadata)

            # add the child node's ID to the next_nodes list
            self.next_nodes.add(child_node.cfg_id)
