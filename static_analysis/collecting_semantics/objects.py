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

    def register_variable(self, variable: str) -> int:
        '''
        Register a variable and return its identifier
        '''

        if variable not in self.variable_table:
            self.variable_table[variable] = {
                'id': self.variable_count,
                'name': variable,
                'value': None,
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

        return self.variable_table[variable]['value'] if variable in self.variable_table else None


class PointState(object):
    '''
    Class representing the state of variables at a program point
    '''

    def __init__(self, _variable_registry: VariableRegistry):
        # also reference the variable registry
        self.variable_registry = _variable_registry

        # variable to store the states of a particular node in the cfg
        self.node_states = dict()

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

    def __add_state_entry(self, node_id: str, variable_name: str, value: Any, iteration: int, is_entry=True) -> None:
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
        # if it is the 0th iteration, create the template tuple and init with undefined values
        if iteration == 0:
            prev_state = self.__generate_state_tuple()
        # if the state is already initialized for that iteration, just get the reference
        elif iteration in self.node_states[node_id][point]:
            prev_state = self.node_states[node_id][point][iteration]
        # else, we need to make a deepcopy of the previous state and use it as the current state
        else:
            prev_state = self.node_states[node_id][point][iteration - 1]

        # convert the tuple to a list (this also makes a new copy, so no need to use deepcopy)
        current_state = list(prev_state)
        # set the value of the variable in the state tuple
        current_state[variable_id] = value

        # add the entry to the state table
        self.node_states[node_id][point][iteration] = tuple(current_state)

    def __generate_state_tuple(self) -> Tuple[Any]:
        '''
        Generate the initial state tuple based on
        the variables present in the variable registry
        '''
        # obtain the variable names and init the state tuple
        variables = self.variable_registry.variable_table.keys()
        state_tuple = tuple(None for _ in variables)

        return state_tuple
