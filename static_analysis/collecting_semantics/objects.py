'''
Auxiliary Objects Module
'''
from typing import Any, Tuple, Union, List, Set, Dict
from enum import Enum


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


class NumericalDomain(Enum):
    '''
    Numerical Domain Lattice Class
    '''

    Top = 'Top'
    Bottom = 'Bottom'


class PointState(object):
    '''
    Class representing the state of variables at a program point
    '''

    def __init__(self, _variable_registry: VariableRegistry, starting_node: str):
        # also reference the variable registry
        self.variable_registry = _variable_registry
        self.starting_node = starting_node

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
        self.node_states[node_id]['entry'][0] = set()
        # in case of exit, we need to have different state sets for each of the next nodes
        # this is why, we include a dictionary of next_node_id -> state_set
        # in this case, if we don't need to specify a next node, we use the wildcard '*'
        self.node_states[node_id]['exit'][0] = {'*': set()}

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

            # if the current state is not equal to the previous state,
            # then the fixed point has not been reached
            if current_state != prev_state:
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
            prev_states.append(prev_state)

        # set the union as the entry set at the current iteration
        self.node_states[node_id]['entry'][self.iteration] = set.union(
            *prev_states)

    def update_node_exit_state(self, node_id: str, next_node_id: str, exit_state_set: Set[Tuple[Any]]) -> None:
        '''
        Update state ordered-pair for the current iteration
        of a given node at it's exit point.
        This exit set might be different for different next nodes of the node
        '''

        # check if the dictionary for the current iteration is initialized or not
        if self.iteration not in self.node_states[node_id]['exit']:
            self.node_states[node_id]['exit'][self.iteration] = dict()

        # write the exit state set for the next node at the current iteration
        self.node_states[node_id]['exit'][self.iteration][next_node_id] = exit_state_set

    def __init_start_node(self, node_id: str) -> None:
        '''
        Init the state of the Start Node (from where the CFG begins)
        '''

        # obtain the initial state tuple
        state_tuple_set = set()
        state_tuple_set.add(self.__generate_state_tuple())

        # set the state_tuple_set
        self.node_states[node_id]['entry'][self.iteration] = state_tuple_set

    def __generate_state_tuple(self) -> Tuple[Any]:
        '''
        Generate the initial state tuple based on
        the variables present in the variable registry
        '''
        # obtain the variable names and init the state tuple
        variables = self.variable_registry.variable_table.keys()
        state_tuple = tuple('btm' for _ in variables)

        return state_tuple
