from django.contrib import admin
from executions.models import Execution, Parameter, Task

# Register your models here.

admin.site.register(Task)
admin.site.register(Parameter)
admin.site.register(Execution)
