import importlib
from typing import Any


def get_tool_class_by_name(name: str) -> Any:
    '''Get tool class by tool name.

    Args:
        name (str): Tool name

    Returns:
        Any: Tool class
    '''
    try:
        tools_module = importlib.import_module(f'tools.tools.{name.lower()}')   # Import tool module
        tool_class = getattr(tools_module, f'{name[0].upper()}{name[1:].lower()}Tool')              # Get tool class
    except (AttributeError, ModuleNotFoundError):                               # Error during import
        tools_module = importlib.import_module('tools.tools.base_tool')         # Get base tool module
        tool_class = getattr(tools_module, 'BaseTool')                          # Get base tool class
    return tool_class
