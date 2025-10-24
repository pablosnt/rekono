"""Base model for input parameters framework.

This module provides the abstract base model for all input parameter types in
the Rekono security testing platform. The InputParameter model serves as the
foundation for concrete parameter implementations like technology and vulnerability
parameters, providing common functionality for task associations and project context.

Architecture:
    The model extends BaseInput to provide input parsing capabilities while adding
    task-based project associations. This design enables project-level access control
    and filtering while supporting multiple project contexts through task relationships.
"""

from functools import cached_property

from framework.models import BaseInput
from projects.models import Project


class InputParameter(BaseInput):
    """Abstract base model for input parameters with task associations.

    Serves as the foundation for all input parameter types in the Rekono platform.
    Provides task association capabilities and project context determination through
    task relationships, enabling project-level access control and parameter filtering.

    Task Association:
        Parameters are associated with tasks through many-to-many relationships,
        allowing parameters to be shared across multiple tasks while maintaining
        project context through the task-target-project relationship chain.

    Project Context:
        The model determines project context by traversing task relationships,
        supporting multiple project associations when parameters are shared
        across tasks in different projects.

    Attributes:
        _project_field (str): Field path for project association through tasks
        Meta: Django meta configuration marking this as an abstract model

    Note:
        This is an abstract model and cannot be instantiated directly. Concrete
        parameter types must inherit from this class and provide specific field
        implementations and validation logic.
    """

    _project_field = "tasks__target__project"

    class Meta:
        """Django Meta class configuration for InputParameter.

        Configures InputParameter as an abstract base class that provides common
        functionality without creating its own database table.

        Attributes:
            abstract (bool): Marks this model as abstract (no database table)
        """

        abstract = True

    @cached_property
    def parent_project(self) -> list[Project]:
        """Get all projects associated with this parameter through tasks.

        Traverses task relationships to determine all projects that have access
        to this parameter, enabling project-level filtering and access control.

        Returns:
            list[Project]: List of all projects associated with this parameter
                          through task relationships

        Note:
            Returns a list because parameters can be associated with tasks
            across multiple projects, providing shared parameter functionality.
        """
        return [task.parent_project for task in self.tasks.all()]
