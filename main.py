import json
from compiler import SolcCompiler

source = '''
pragma solidity >0.4.99 <0.6.0;
 
  library OldLibrary {
    function someFunction(uint8 a) public returns(bool);
  }
 
  contract NewContract {
    function f(uint8 a) public returns (bool) {
        return OldLibrary.someFunction(a);
    }
  }
'''

compiler = SolcCompiler(source)
output = compiler.compile()
contracts = output.get_contracts_list()
print(contracts)
ast = output.get_ast(contracts[1])
print(ast)
with open('ast.json', 'w', encoding='utf8') as f:
    json.dump(ast, f, indent=4)
