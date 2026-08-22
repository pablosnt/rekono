"""Role-based access control of the Rekono platform.

The roles define the model permissions that each user gets, and are assigned to
Django auth groups after the migrations. On top of them, the permission classes
enforce the project membership and the ownership of the personal resources, so a
user can only reach the data of their own projects.
"""
