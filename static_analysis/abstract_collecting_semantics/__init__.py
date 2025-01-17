'''
The Collecting Semantics Analysis in the Interval Abstract Domain
'''
from java_wrapper import apron, java
from control_flow_graph import ControlFlowGraph
from static_analysis.abstract_collecting_semantics.objects import VariableRegistry, PointState
import static_analysis.abstract_collecting_semantics.builder as builder
from time import sleep


class AbstractCollectingSemanticsAnalysis(object):
    '''
    Class defining the collecting semantics analysis on the Interval Abstract Domain
    '''

    def __init__(self, cfg: ControlFlowGraph, starting_node: str, ending_node: str, _java_class_path: str, _java_lib_path=None):
        '''
        Constructor
        '''

        # Import APRON Classes
        self.manager = apron.Box()

        self.cfg = cfg
        self.starting_node = starting_node
        self.ending_node = ending_node

        self.variable_registry = VariableRegistry()
        self.constant_registry = VariableRegistry()
        self.point_state = PointState(
            self.variable_registry, self.starting_node, self.manager)

    def compute(self) -> None:
        '''
        Compute the collecting semantics analysis
        '''

        # first compute on the expression statements
        # obtain the variables to track the state of
        self.__compute_variables()
        print(self.variable_registry.variable_table.keys())

        # compute the abstract collecting semantics in the Interval Abstract Domain
        self.__compute_abstract_collecting_semantics()

        # print the output for all the iterations
        for node in self.point_state.node_states.keys():
            for i in range(1, self.point_state.iteration+1):
                print('ENTRY', i, node, java.Arrays.toString(self.point_state.get_node_state_set(
                    node, i, True).toBox(self.manager)))
                # print('EXIT', i, node, self.point_state.get_node_state_set(
                #     node, i, False))

    def __compute_variables(self) -> None:
        '''
        Compute and enroll all the variables present in the CFG
        '''

        visited = set()

        def traverse(node_id, visited: set, cfg: ControlFlowGraph):
            '''
            Traverse the Graph and Compute the GEN and KILL functions
            '''

            if node_id in visited:
                return

            # add to visited set
            visited.add(node_id)

            # get node instance / object
            node = cfg.cfg_metadata.get_node(node_id)

            # register the node on the PointState instance
            self.point_state.register_node(node_id)

            # register the variables obtained from the node
            variables = builder.get_variables(node)
            for variable in variables:
                self.variable_registry.register_variable(variable)

            print("VARIABLE-REGISTRY", node_id, variables)

            if node_id != self.ending_node:
                for child_id in node.next_nodes:
                    child_node = cfg.cfg_metadata.get_node(child_id)

                    traverse(child_node.cfg_id, visited, cfg)

        traverse(self.starting_node, visited, self.cfg)

        self.point_state.init_node_states()

    def __compute_abstract_collecting_semantics(self) -> None:
        '''
        Compute the Collecting Semantics
        '''

        def traverse(node_id, visited: set, cfg: ControlFlowGraph):
            '''
            Traverse the Graph and Compute the Collecting Semantics
            '''

            if node_id in visited:
                return

            # add to visited set
            visited.add(node_id)

            print("COLLSEM-TRV", node_id)

            # get node instance / object
            node = cfg.cfg_metadata.get_node(node_id)

            # get the previous nodes list of the node
            prev_nodes = list(node.prev_nodes.keys())

            # 1. udpate the entry state set for the node
            self.point_state.update_node_entry_state(node_id, prev_nodes)
            entry_set = self.point_state.get_node_state_set(
                node_id, self.point_state.iteration)

            # 1.1 Obtain the exit set of previous iteration
            exit_sets = self.point_state.get_node_state_set(
                node_id, self.point_state.iteration-1, False, '*', True)

            # 2. process the node semantics and generate the exit state sets for it's next nodes
            exit_sets = builder.generate_exit_sets(
                node, entry_set, exit_sets, self.variable_registry, self.constant_registry, self.manager)

            # 3. udpate the exit state set for the node
            # (EDGE CASE: for ending node, we will use the next node as '*')
            for next_node_id, exit_set in exit_sets.items():
                self.point_state.update_node_exit_state(
                    node_id, next_node_id, exit_set)

            if node_id != self.ending_node:
                for child_id in node.next_nodes:
                    child_node = cfg.cfg_metadata.get_node(child_id)

                    traverse(child_node.cfg_id, visited, cfg)

        while True:
            visited = set()
            self.point_state.start_computation_round()
            print('Start Iter:', self.point_state.iteration)
            traverse(self.starting_node, visited, self.cfg)

            sleep(0.2)

            if self.point_state.is_fixed_point_reached():
                break
