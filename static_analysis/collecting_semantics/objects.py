'''
Auxiliary Objects Module
'''


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
            self.variable_table[variable] = self.variable_count
            self.variable_count += 1

        return self.variable_table[variable]

    def get_variable_id(self, variable: str) -> int:
        '''
        Get the identifier of a variable
        '''

        return self.variable_table[variable] if variable in self.variable_table else -1
