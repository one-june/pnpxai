from typing import List, Dict

import torch
from torch import nn, Tensor, fx
from pnpxai.explainers.rap import rules
from pnpxai.explainers.utils.operation_graph import OperationGraph, OperationNode

SUPPORTED_MODULES: Dict[type[nn.Module], type[rules.RelProp]] = {
    nn.Sequential: rules.Sequential,
    nn.ReLU: rules.ReLU,
    nn.Dropout: rules.Dropout,
    nn.MaxPool2d: rules.MaxPool2d,
    nn.AdaptiveAvgPool2d: rules.AdaptiveAvgPool2d,
    nn.AvgPool2d: rules.AvgPool2d,
    nn.BatchNorm2d: rules.BatchNorm2d,
    nn.Linear: rules.Linear,
    nn.Conv2d: rules.Conv2d,
}

SUPPORTED_FUNCTIONS: Dict[callable, type[rules.RelProp]] = {
    torch.add: rules.Add,
    torch.flatten: rules.Flatten,
}
SUPPORTED_BUILTINS: Dict[str, type[rules.RelProp]] = {
    'add': rules.Add,
    'flatten': rules.Flatten,
}


class RelativeAttributePropagation():
    def __init__(self, model: nn.Module):
        self.model = model
        self.graph = OperationGraph(model)

        self._assign_rules_and_hooks(self.graph.root)

    def _assign_rules_and_hooks(self, node: OperationNode):
        if node.is_module:
            layer = node.method
            if type(layer) in SUPPORTED_MODULES and not (hasattr(layer, 'rule')):
                rule = SUPPORTED_MODULES[type(layer)]
                layer.rule: rules.RelProp = rule(layer)
                layer.register_forward_hook(layer.rule.forward_hook)

        for next_node in node.next_nodes:
            self._assign_rules_and_hooks(next_node)

    def relprop(self, r: Tensor) -> Tensor:
        def _relprop(node: OperationNode):
            if node.is_output:
                return r.clone()

            cur_relprops = []
            for next_node in node.next_nodes:
                method = node.method
                next_relprop = None
                args_list = [
                    prev_node.method.rule.Y for prev_node in node.prev_nodes if prev_node.is_module]
                args = args_list[0] if len(args_list) == 1 else args_list
                rule = None
                if node.is_placeholder:
                    rule = rules.RelProp()
                elif node.is_module and type(method) in SUPPORTED_MODULES:
                    rule = method.rule
                elif node.is_function:
                    if type(method) in SUPPORTED_FUNCTIONS:
                        rule = SUPPORTED_FUNCTIONS[type(method)](method)
                    else:
                        built_in_name = str(method)[1:-1].split(' ')
                        if len(built_in_name) >= 3 and built_in_name[2] in SUPPORTED_BUILTINS:
                            rule = SUPPORTED_BUILTINS[built_in_name[2]]()

                if rule is None:
                    raise NotImplementedError(f'Unsupported node: {node}')
                print("BEFORE: ", node, rule)
                next_relprop = _relprop(next_node)
                print("AFTER: ", node, rule)
                cur_relprop = rule.relprop(next_relprop, args)
                cur_relprops.append(cur_relprop)

            return sum(cur_relprops) if len(cur_relprops) > 1 else cur_relprops[0]

        return _relprop(self.graph.root)
