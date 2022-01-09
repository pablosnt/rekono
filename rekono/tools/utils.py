import importlib


def get_tool_class_by_name(name):
    try:
        tools_module = importlib.import_module(f'tools.tools.{name.lower()}')
        tool_class = f'{name[0].upper()}{name[1:].lower()}Tool'
        tool_class = getattr(tools_module, tool_class)
    except (AttributeError, ModuleNotFoundError):
        tools_module = importlib.import_module('tools.tools.base_tool')
        tool_class = getattr(tools_module, 'BaseTool')
    return tool_class
