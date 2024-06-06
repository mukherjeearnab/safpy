import json
from compiler import SolCompiler
from control_flow_graph import ControlFlowGraph
from static_analysis.dataflow_analysis.avl_expr import AvailableExpressionAnalysis
source = '''
pragma solidity ^0.4.0;

contract c {
    //int a = 10;
    int b = 12;

    function run(int a, int b) {
        int x = a + b;
        int y = a * b;

        while (y > a + b) {
            a = a - 1;
            x = a + b;
        }
    }
}
/*
contract d {
    int a = 0;
}*/

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
cfg.generate_dot_bottom_up()

avl_expr = AvailableExpressionAnalysis(
    cfg, 'FunctionEntry_0', 'FunctionExit_0')

avl_expr.compute()
