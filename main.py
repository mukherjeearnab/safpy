import json
from compiler import SolCompiler
from control_flow_graph import ControlFlowGraph
source = '''
pragma solidity ^0.4.0;

contract c {
    int a = 10;
    int b = 12;

    function run() {
        if (a == 10) {
        b += 1;
        } else {
            b -= 1;
        }
    }
}

'''

compiler = SolCompiler(source)
output = compiler.compile()
contracts = output.get_contracts_list()
print(contracts)
ast = output.get_ast(contracts[0])

print(ast.keys())

with open('./gen/ast.json', 'w', encoding='utf8') as f:
    json.dump(ast, f, indent=4)


cfg = ControlFlowGraph(source, ast)
cfg.build_cfg()
