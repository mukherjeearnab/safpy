'''
Auxiliary Objects Module
'''
from typing import Any, Tuple
from copy import deepcopy


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

        return self.variable_table[variable] if variable in self.variable_table else -1

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

    def __init__(self, _variable_registry: VariableRegistry):
        # also reference the variable registry
        self.variable_registry = _variable_registry

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
        self.node_states[node_id]['entry'][0] = self.__generate_state_tuple()
        self.node_states[node_id]['exit'][0] = self.__generate_state_tuple()

    def get_node_var_state(self, node_id: str, iteration: int, is_entry=True) -> None:
        '''
        get the entry of a variable's state for a given node
        '''

        point = 'entry' if is_entry else 'exit'

        if node_id not in self.node_states:
            raise Exception(f"Node with id {node_id} is not registered!")

        if iteration not in self.node_states[node_id][point]:
            raise Exception(
                f"State for Iteration {iteration} is not available for node {node_id}!")

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
            current_state = self.node_states[node_id]['exit'][self.iteration]
            prev_state = self.node_states[node_id]['exit'][self.iteration - 1]

            # if the current state is not equal to the previous state,
            # then the fixed point has not been reached
            if current_state != prev_state:
                return False

        # if everything passes, return True
        return True

    def update_node_var_state(self, node_id: str, variable_name: str, value: Any, is_entry=True) -> None:
        '''
        Add an entry of a variable's state for a given node
        '''

        point = 'entry' if is_entry else 'exit'

        # get the variable's index / id from the variable registry
        variable_id = self.variable_registry.get_id(variable_name)

        # if the variable is not registered, raise an exception
        if variable_id == -1:
            raise Exception(f"Variable {variable_name} is not registered!")

        # obtain the previous iteration's entry,
        # if the state is already initialized for that iteration, just get the reference
        if self.iteration in self.node_states[node_id][point]:
            prev_state = self.node_states[node_id][point][self.iteration]
        # else, we need to make a deepcopy of the previous state and use it as the current state
        else:
            prev_state = self.node_states[node_id][point][self.iteration - 1]

        # convert the tuple to a list (this also makes a new copy, so no need to use deepcopy)
        current_state = list(prev_state)
        # set the value of the variable in the state tuple
        current_state[variable_id] = value

        # add the entry to the state table
        self.node_states[node_id][point][self.iteration] = tuple(current_state)

    def __generate_state_tuple(self) -> Tuple[Any]:
        '''
        Generate the initial state tuple based on
        the variables present in the variable registry
        '''
        # obtain the variable names and init the state tuple
        variables = self.variable_registry.variable_table.keys()
        state_tuple = tuple(None for _ in variables)

        return state_tuple
