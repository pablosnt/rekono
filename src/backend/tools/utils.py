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
        # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
        tools_module = importlib.import_module(f'tools.tools.{name.lower().replace(" ", "_")}')   # Import tool module
        # Get tool class
        tool_class = getattr(tools_module, name[0].upper() + name[1:].lower().replace(' ', ''))
    except (AttributeError, ModuleNotFoundError):                               # Error during import
        tools_module = importlib.import_module('tools.tools.base_tool')         # Get base tool module
        tool_class = getattr(tools_module, 'BaseTool')                          # Get base tool class
    return tool_class
