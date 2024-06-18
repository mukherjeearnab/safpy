'''
Auxiliary Objects Module
'''
from typing import Any, Tuple, Union, List, Set, Dict
from enum import Enum
import jpype

# MpqScalar = jpype.JClass("apron.MpqScalar")
# Linterm0 = jpype.JClass("apron.Linterm0")
# Linexpr0 = jpype.JClass("apron.Linexpr0")
# Texpr0BinNode = jpype.JClass("apron.Texpr0BinNode")
# Texpr0CstNode = jpype.JClass("apron.Texpr0CstNode")
# Texpr0Node = jpype.JClass("apron.Texpr0Node")
# Texpr0Intern = jpype.JClass("apron.Texpr0Intern")
# Texpr0DimNode = jpype.JClass("apron.Texpr0DimNode")


class VariableRegistry(object):
    '''
    Class representing a variable registry to store variables and
    assign them IDs to recognize
    '''

    def __init__(self):
        self.variable_table = dict()
        self.variable_count = 0

    def register_variable(self, variable: str, value=None) -> int:
        '''
        Register a variable and return its identifier
        '''

        if variable not in self.variable_table:
            self.variable_table[variable] = {
                'id': self.variable_count,
                'name': variable,
                'value': value
            }
            self.variable_count += 1

        return self.variable_table[variable]

    def get_id(self, variable: str) -> int:
        '''
        Get the identifier of a variable
        '''

        return self.variable_table[variable]['id'] if variable in self.variable_table else -1

    def get_value(self, variable: str) -> Any:
        '''
        Get the value of a variable
        '''

        if variable not in self.variable_table:
            raise Exception(f'Variable {variable} not registered!')

        return self.variable_table[variable]['value']

    def set_value(self, variable: str, value: Any) -> None:
        '''
        Set the value of a variable
        '''

        if variable not in self.variable_table:
            raise Exception(f'Variable {variable} not registered!')

        self.variable_table[variable]['value'] = value


class PointState(object):
    '''
    Class representing the state of variables at a program point
    '''

    def __init__(self, _variable_registry: VariableRegistry, starting_node: str, apron_manager: jpype.JClass):
        # also reference the variable registry
        self.variable_registry = _variable_registry
        self.starting_node = starting_node

        # init the APRON manager as the Box, i.e., the Interval Domain
        self.manager = apron_manager

        # variable to store the states of a particular node in the cfg
        self.node_states = dict()

        # the iteration counter variable to keet record of the iterations taken
        self.iteration = 0

    def register_node(self, node_id: str) -> None:
        '''
        Register a node and initialize the state
        for the entry and exit points of the node
        '''

        # if the node is already registered, raise an exception
        if node_id in self.node_states:
            raise Exception(f"Node with id {node_id} already registered!")

        # init the state table
        self.node_states[node_id] = {
            'entry': dict(),
            'exit': dict()
        }

        # initialize the state table for the entry and exit points
        self.node_states[node_id]['entry'][0] = None
        # in case of exit, we need to have different state sets for each of the next nodes
        # this is why, we include a dictionary of next_node_id -> state_set
        # in this case, if we don't need to specify a next node, we use the wildcard '*'
        self.node_states[node_id]['exit'][0] = {'*': None}

    def get_node_state_set(self, node_id: str, iteration: int, is_entry=True, next_node='*') -> Union[Set[Tuple[int]], Dict[str, Set[Tuple[int]]]]:
        '''
        get the entry of a variable's state for a given node
        '''

        point = 'entry' if is_entry else 'exit'

        if node_id not in self.node_states:
            raise Exception(f"Node with id {node_id} is not registered!")

        if iteration not in self.node_states[node_id][point]:
            raise Exception(
                f"State for Iteration {iteration} is not available for node {node_id}!")

        # for exit states, we need to also include the next node for which we fetch the exit node
        if not is_entry:
            if next_node not in self.node_states[node_id][point][iteration]:
                if '*' in self.node_states[node_id][point][iteration]:
                    return self.node_states[node_id][point][iteration]['*']
                else:
                    return self.node_states[node_id][point][iteration]
            else:
                return self.node_states[node_id][point][iteration][next_node]

        return self.node_states[node_id][point][iteration]

    def start_computation_round(self) -> None:
        '''
        Start the computation round by imcrementing the iteration counter
        '''

        self.iteration += 1

    def is_fixed_point_reached(self) -> bool:
        '''
        Check if the fixed point is reached or not
        '''

        # base case
        # if the iteration is 0, return False
        if self.iteration < 1:
            return False

        # iterate over all the nodes, and check their exit states
        for node_id in self.node_states:
            current_state = self.node_states[node_id]['entry'][self.iteration]
            prev_state = self.node_states[node_id]['entry'][self.iteration - 1]

            # EDGE CASE: prev state is None
            if prev_state is None:
                return False

            # if the current state is not equal to the previous state,
            # then the fixed point has not been reached
            # in this case we use the apron method isEqual to check the similarity
            if not current_state.isEqual(self.manager, prev_state):
                return False

        # if everything passes, return True
        return True

    def update_node_entry_state(self, node_id: str, prev_nodes: List[str]) -> None:
        '''
        Update state ordered-pair for the current iteration
        of a given node at it's entry point.
        '''

        # edge case: node is the starting node
        if node_id == self.starting_node:
            self.__init_start_node(node_id)

            return

        # obtain the exit state ordered-pair sets from the previous nodes
        prev_states = []
        for prev_node in prev_nodes:
            prev_state = self.get_node_state_set(
                prev_node, self.iteration - 1, is_entry=False, next_node=node_id)
            if prev_state is not None:
                prev_states.append(prev_state)

        # if previous states is empty, then generate a new state
        if len(prev_states) == 0:
            abs_state = self.__generate_state_tuple()
        else:
            # set the union as the entry set at the current iteration
            abs_state = prev_states.pop()
            for state in prev_states:
                # use the apron method to join (union of) the two states
                abs_state = abs_state.joinCopy(self.manager, state)

        self.node_states[node_id]['entry'][self.iteration] = abs_state

    def update_node_exit_state(self, node_id: str, next_node_id: str, exit_state: Set[jpype.JClass]) -> None:
        '''
        Update state for the current iteration
        of a given node at it's exit point.
        This exit set might be different for different next nodes of the node
        '''

        # check if the dictionary for the current iteration is initialized or not
        if self.iteration not in self.node_states[node_id]['exit']:
            self.node_states[node_id]['exit'][self.iteration] = dict()

        # write the exit state set for the next node at the current iteration
        self.node_states[node_id]['exit'][self.iteration][next_node_id] = exit_state

    def __init_start_node(self, node_id: str) -> None:
        '''
        Init the state of the Start Node (from where the CFG begins)
        '''

        # obtain the initial state tuple
        state_tuple = self.__generate_state_tuple()

        # set the state_tuple_set
        self.node_states[node_id]['entry'][self.iteration] = state_tuple

    def __generate_state_tuple(self) -> Tuple[Any]:
        '''
        Generate the initial abstract state tuple based on
        the variables present in the variable registry
        '''

        # Import APRON Classes
        Abstract0 = jpype.JClass("apron.Abstract0")
        Interval = jpype.JClass("apron.Interval")

        # obtain the variable names and init the state tuple
        variables = self.variable_registry.variable_table.keys()
        int_variables_count = len(variables)
        real_variables_count = 0

        # init the Inverval for every variable
        # box_state = [Interval() for _ in variables]
        box_state = Interval[int_variables_count]
        for i in range(int_variables_count):
            box_state[i] = Interval()

        # generate the level 0 abstract state
        state = Abstract0(self.manager, int_variables_count,
                          real_variables_count, box_state)

        return state
