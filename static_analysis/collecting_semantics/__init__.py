'''
The Collecting Semantics Analysis
'''
from typing import Union
from control_flow_graph import ControlFlowGraph
from static_analysis.collecting_semantics.objects import VariableRegistry, PointState
import static_analysis.collecting_semantics.builder as builder
# from static_analysis.dataflow_analysis.avl_expr.expr_builder import expr_builder
# from static_analysis.dataflow_analysis.avl_expr.expr_builder.objects import Expression, ExpressionStatement


class CollectingSemanticsAnalysis(object):
    '''
    Class defining the collecting semantics analysis
    '''

    def __init__(self, cfg: ControlFlowGraph, starting_node: str, ending_node: str):
        '''
        Constructor
        '''

        self.cfg = cfg
        self.starting_node = starting_node
        self.ending_node = ending_node

        self.variable_registry = VariableRegistry()
        self.constant_registry = VariableRegistry()
        self.point_state = PointState(
            self.variable_registry, self.starting_node)

    def compute(self) -> None:
        '''
        Compute the collecting semantics analysis
        '''

        # first compute on the expression statements
        # obtain the variables to track the state of
        self.__compute_variables()
        print(self.variable_registry.variable_table.keys())

        # initialize the node variable states
        self.__init_node_var_states()

        '''
        [DONE] next, we start with traversing the cfg, visiting each node,
        [DONE] inti the state of each of the node variables
        and compute the variable states at the entry and exit of the node
        (do this until for each node's (exit point) previous state is exactly the same as the current state)
        '''

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

    def __compute_collecting_semantics(self) -> None:
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

            # get node instance / object
            node = cfg.cfg_metadata.get_node(node_id)

            # get the previous nodes list of the node
            prev_nodes = list(node.prev_nodes.keys())

            # 1. udpate the entry state set for the node
            self.point_state.update_node_entry_state(node_id, prev_nodes)

            # 2. process the node semantics and generate the exit state sets for it's next nodes

            # 3. udpate the exit state set for the node
            # (EDGE CASE: for ending node, we will use the next node as '*')

            # update the variable in question, if changed
            '''
            This should work like, 
            [DONE] first, we obtain the values of the existing variables from exit node of the previous nodes:
                1. obtain the exit of the previous nodes
                2. apply the meet operator to these exit states
                3. set this new one as the entry of the current (update entry state)
            second, compute the expression (if any based on the entry state values)
            third, update the exit state of the current node based on the computed expression
                1. check if exit node's current value is different from the evaluated expression
                2. if yes, update the exit state of the current node
                3. else continue to next nodes
            '''

            print("COLSEM-COMPUT", node_id)

            if node_id != self.ending_node:
                for child_id in node.next_nodes:
                    child_node = cfg.cfg_metadata.get_node(child_id)

                    traverse(child_node.cfg_id, visited, cfg)

        visited = set()
        while True:
            self.point_state.start_computation_round()
            traverse(self.starting_node, visited, self.cfg)

            if self.point_state.is_fixed_point_reached():
                break

    def __compute_avl_expr(self) -> None:
        '''
        Compute the GEN and KILL functions for all the nodes
        '''

        worklist = set()
        visited = set()

        # initialize worklist with initial node
        worklist.add(self.starting_node)

        while len(worklist) != 0:
            node_id = worklist.pop()

            print('WORKLIST PROCESS', node_id)

            entries, exit_set = list(), set()

            node = self.cfg.cfg_metadata.get_node(node_id)

            #######################
            # 1. compute the entry set
            for prev_id in node.prev_nodes:
                entries.append(self.get_exit(prev_id))

            # in this case, we need intersection of all incoming branches
            entry = set.intersection(*entries)

            # finally update the entry set
            self.add_entry(node_id, entry)

            #######################
            # 2. compute the exit set (based on the transfer function)
            exit_set = set.difference(entry, self.get_kill(node_id))
            exit_set = exit_set.union(self.get_gen(node_id))

            #######################
            # 3. if exit set is changed OR node is processed first time,
            # add the next nodes of the node to worklist
            if exit_set != self.get_exit(node_id) or node_id not in visited:
                visited.add(node_id)

                self.add_exit(node_id, exit_set)

                if node_id != self.ending_node:
                    for next_id in node.next_nodes:
                        worklist.add(next_id)
