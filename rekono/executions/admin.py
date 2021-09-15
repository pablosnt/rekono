from django.contrib import admin
from executions.models import Execution, Parameter, Request

# Register your models here.

admin.site.register(Request)
admin.site.register(Parameter)
admin.site.register(Execution)
