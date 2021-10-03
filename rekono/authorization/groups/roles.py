from django.db import models


class Role(models.IntegerChoices):
    ADMIN = 1
    AUDITOR = 2
    READER = 3


DEFAULT_GROUPS = {
    Role.ADMIN: [
        # Users
        'add_user',
        'change_user',
        'delete_user',
        'view_user',
        # Projects
        'add_project',
        'change_project',
        'delete_project',
        'view_project',
        'add_target',
        'delete_target',
        'view_target',
        'add_targetport',
        'delete_targetport',
        'view_targetport',
        # Executions
        'add_request',
        'delete_request',
        'view_request',
        'view_execution',
        # Findings
        'change_osint',
        'view_osint',
        'change_host',
        'view_host',
        'change_enumeration',
        'view_enumeration', 
        'change_httpendpoint',
        'view_httpendpoint',
        'change_technology',
        'view_technology',
        'change_vulnerability',
        'view_vulnerability',
        'change_exploit',
        'view_exploit',
        # Processes
        'add_process',
        'change_process',
        'delete_process',
        'view_process',
        'add_step',
        'change_step',
        'delete_step',
        'view_step',
        # Tools
        'view_tool',
        'view_intensity',
        'view_configuration',
        'view_input',
        'view_output',
    ],
    Role.AUDITOR: [
        # Projects
        'view_project',
        'add_target',
        'delete_target',
        'view_target',
        'add_targetport',
        'delete_targetport',
        'view_targetport',
        # Executions
        'add_request',
        'delete_request',
        'view_request',
        'view_execution',
        # Findings
        'change_osint',
        'view_osint',
        'change_host',
        'view_host',
        'change_enumeration',
        'view_enumeration',        
        'change_httpendpoint',
        'view_httpendpoint',
        'change_technology',
        'view_technology',
        'change_vulnerability',
        'view_vulnerability',
        'change_exploit',
        'view_exploit',
        # Processes
        'add_process',
        'change_process',
        'delete_process',
        'view_process',
        'add_step',
        'change_step',
        'delete_step',
        'view_step',
        # Tools
        'view_tool',
        'view_intensity',
        'view_configuration',
        'view_input',
        'view_output',
    ],
    Role.READER: [
        # Projects
        'view_project',
        'view_target',
        'view_targetport',
        # Executions
        'view_request',
        'view_execution',
        # Findings
        'view_osint',
        'view_host',
        'view_enumeration',
        'view_httpendpoint',
        'view_technology',
        'view_vulnerability',
        'view_exploit',
    ]
}
