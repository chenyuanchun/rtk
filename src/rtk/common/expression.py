import re
from itertools import count
from collections import namedtuple


CompiledVariable = namedtuple('CompiledVariable', 'config_var standard_var')
DEFAULT_RESOLVER = 'default'


def _resolve_variable(config_var: str, data_context: dict) -> str:
    return data_context.get(config_var, '')


class Expression:
    """Python expression with user defined variables
    valid variable format: ${var} or ${var.attr}
    complex variable needs the user to supply a variable resolver compliant to the default one '_resolve_variable'"""

    VARIABLE_PATTERN = re.compile('\${[^\}]+\}')
    _resolver_registry = {DEFAULT_RESOLVER: _resolve_variable}

    def __init__(self, string: str):
        self._expression = string
        self._var_idx = count(1)
        self._variables = []
        self._compiled = Expression.VARIABLE_PATTERN.sub(self._standardize_vars, string)

    def _standardize_vars(self, match):
        _variable = match.group()
        assert isinstance(_variable, str) and len(_variable) > 3
        _config_var = _variable[2:-1].strip()
        _standard_var = ''.join(('__var_', str(next(self._var_idx))))
        self._variables.append(CompiledVariable(_config_var, _standard_var))
        return _standard_var

    @staticmethod
    def _get_var_resolver(var_name):
        _base_var = var_name.split('.', 1)[0]
        ret = Expression._resolver_registry.get(_base_var)
        return ret or Expression._resolver_registry[DEFAULT_RESOLVER]

    def __call__(self, functions=None, **data_context):
        _actual_values = {}
        for _var in self._variables:
            _resolve_func = Expression._get_var_resolver(_var.config_var)
            _actual_values[_var.standard_var] = _resolve_func(_var.config_var, {**data_context})

        _globals = functions or globals()
        return eval(self._compiled, _globals, _actual_values)
