"""Django app configuration for input_types module.

Configures the input_types Django application through BaseApp, which loads
the default InputType fixture data into the database after migrations.
"""

from django.apps import AppConfig

from framework.apps import BaseApp


class InputTypesConfig(BaseApp, AppConfig):
    """Django app configuration for input_types.

    Extends BaseApp to inherit automatic fixture loading, populating the
    default InputType records after migrations complete.

    Attributes:
        name (str): The name of the Django app.
    """

    name = "input_types"
