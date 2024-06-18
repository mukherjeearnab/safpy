import json
from compiler import SolCompiler
from control_flow_graph import ControlFlowGraph
# from static_analysis.dataflow_analysis.avl_expr import AvailableExpressionAnalysis
# from static_analysis.collecting_semantics import CollectingSemanticsAnalysis
from static_analysis.abstract_collecting_semantics import AbstractCollectingSemanticsAnalysis

source = '''
pragma solidity ^0.4.0;

contract c {
    //int a = 10;
    int b = 12;

    function run() {
        int a = 1;
        int b = 1;
        
        for (int i = 0; i < 3; i++) {
            a = a + b;
        }

        int d = a + b;
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

csem = AbstractCollectingSemanticsAnalysis(
    cfg, 'FunctionEntry_0', 'FunctionExit_0', '/home/arnab/.apron_bin/apron.jar')

csem.compute()
