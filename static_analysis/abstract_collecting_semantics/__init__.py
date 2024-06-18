'''
The Collecting Semantics Analysis in the Interval Abstract Domain
'''
import jpype
from jpype import startJVM, shutdownJVM, addClassPath, JClass, JInt
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
        # init jpype jvm
        self.__init_jpype(_java_class_path, _java_lib_path)

        # Import APRON Classes
        Box = jpype.JClass("apron.Box")
        self.manager = Box()

        self.cfg = cfg
        self.starting_node = starting_node
        self.ending_node = ending_node

        self.variable_registry = VariableRegistry()
        self.constant_registry = VariableRegistry()
        self.point_state = PointState(
            self.variable_registry, self.starting_node, self.manager)

    def __init_jpype(self, class_path: str, library_path: str):
        '''
        Initialize the JPype JVM with the Classpath and Java Library paths
        '''

        # Initialize the JVM and add the Apron library to the classpath
        # addClassPath(class_path)

        lib_path = jpype.getDefaultJVMPath() if library_path is None else library_path
        print(lib_path)
        startJVM(classpath=['/home/arnab/.apron_bin/apron.jar',
                 '/home/arnab/.apron_bin/gmp.jar'])
        # f"-Djava.library.path=/usr/local/lib;/usr/lib;/home/arnab/.apron_bin")  # ,
        #  f"-Djava.class.path={class_path}:/home/arnab/.apron_bin/gmp.jar")

    def compute(self) -> None:
        '''
        Compute the collecting semantics analysis
        '''

        # first compute on the expression statements
        # obtain the variables to track the state of
        self.__compute_variables()
        print(self.variable_registry.variable_table.keys())

        Arrays = jpype.JClass("java.util.Arrays")

        self.__compute_abstract_collecting_semantics()
        for node in self.point_state.node_states.keys():
            for i in range(self.point_state.iteration, self.point_state.iteration+1):
                print('ENTRY', i, node, Arrays.toString(self.point_state.get_node_state_set(
                    node, i, True).toBox(self.manager)))
                print('EXIT', i, node, self.point_state.get_node_state_set(
                    node, i, False))

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
                node_id, self.point_state.iteration-1, False)

            # 2. process the node semantics and generate the exit state sets for it's next nodes
            exit_sets = builder.generate_exit_sets(
                node, entry_set, exit_sets, self.variable_registry, self.constant_registry, self.manager)

            # 3. udpate the exit state set for the node
            # (EDGE CASE: for ending node, we will use the next node as '*')
            for next_node_id, exit_set in exit_sets.items():
                self.point_state.update_node_exit_state(
                    node_id, next_node_id, exit_set)

            '''
            This should work like,
            [DONE] first, we obtain the values of the existing variables from exit node of the previous nodes:
                1. obtain the exit of the previous nodes
                2. apply the meet operator to these exit states
                3. set this new one as the entry of the current (update entry state)
            [DONE] second, compute the expression (if any based on the entry state values)
            [DONE] third, update the exit state of the current node based on the computed expression
                1. check if exit node's current value is different from the evaluated expression
                2. if yes, update the exit state of the current node
                3. else continue to next nodes
            '''

            # print("COLlSEM-COMPUT", node_id)

            if node_id != self.ending_node:
                for child_id in node.next_nodes:
                    child_node = cfg.cfg_metadata.get_node(child_id)

                    traverse(child_node.cfg_id, visited, cfg)

        while True:
            visited = set()
            self.point_state.start_computation_round()
            print('Start Iter:', self.point_state.iteration)
            traverse(self.starting_node, visited, self.cfg)

            # print(self.point_state.iteration, 'VariableDeclarationStatement_1', self.point_state.get_node_state_set(
            #     'VariableDeclarationStatement_1', self.point_state.iteration, True))

            sleep(1)

            if self.point_state.is_fixed_point_reached():
                break
