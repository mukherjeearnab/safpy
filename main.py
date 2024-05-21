import json
from compiler import SolCompiler
from control_flow_graph import ControlFlowGraph
source = '''
pragma solidity ^0.4.0;

contract c {
    int a = 10;
    int b = 12;

    function run() {
        int m = 20;
        if (a == 10) {
        b+=1;
        m = b - 2;
        } else {
            b -= 1;
            b -= a-m;
        }
        int n = 10;
        m += n;
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
cfg.generate_dot()
# cfg.generate_dot_bottom_up()
