import importlib


def get_tool_class_by_name(name):
    try:
        tools_module = importlib.import_module(
            f'tools.tools.{name}'
        )
        tool_class = name.capitalize() + 'Tool'
        tool_class = getattr(tools_module, tool_class)
    except (AttributeError, ModuleNotFoundError):
        tools_module = importlib.import_module('tools.tools.base_tool')
        tool_class = getattr(tools_module, 'BaseTool')
    return tool_class


def get_keys_from_argument(argument: str) -> list:
    if '{' in argument and '}' in argument:
        aux = argument.split('{')
        return [k.split('}')[0] for k in aux if '}' in k]
    return []
