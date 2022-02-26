from typing import Any, Dict


class BaseInput:
    '''Class to be extended by all the objects that can be used in tool executions as argument.'''

    def filter(self, input: Any) -> bool:
        '''Check if this instance is valid based on input filter.

        Args:
            input (Any): Tool input whose filter will be applied

        Returns:
            bool: Indicate if this instance match the input filter or not
        '''
        return True

    def parse(self, accumulated: Dict[str, Any] = {}) -> Dict[str, Any]:
        '''Get useful information from this instance to be used in tool execution as argument.

        To be implemented by subclasses.

        Args:
            accumulated (Dict[str, Any], optional): Information from other instances of the same type. Defaults to {}.

        Returns:
            Dict[str, Any]: Useful information for tool executions, including accumulated if setted
        '''
        return {}                                                               # pragma: no cover
