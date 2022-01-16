from django.db import models


class Role(models.TextChoices):
    '''User role names.'''

    ADMIN = 'Admin'
    AUDITOR = 'Auditor'
    READER = 'Reader'


# Permission association for each user role
ROLES = {
    Role.ADMIN: [
        'add_user', 'change_user', 'delete_user', 'view_user',                  # Users
        'add_project', 'change_project', 'delete_project', 'view_project',      # Projects
        'add_target', 'delete_target', 'view_target',                           # Targets
        'add_targetport', 'delete_targetport', 'view_targetport',               # Target ports
        'add_targetendpoint', 'delete_targetendpoint', 'view_targetendpoint',   # Target endpoints
        'add_task', 'delete_task', 'view_task',                                 # Tasks
        'view_execution',                                                       # Executions
        'add_osint', 'delete_osint', 'view_osint',                              # OSINT
        'add_host', 'delete_host', 'view_host',                                 # Hosts
        'add_enumeration', 'delete_enumeration', 'view_enumeration',            # Enumerations
        'add_endpoint', 'delete_endpoint', 'view_endpoint',                     # Endpoints
        'add_technology', 'delete_technology', 'view_technology',               # Technologies
        'add_vulnerability', 'change_vulnerability', 'delete_vulnerability', 'view_vulnerability',  # Vulnerabilities
        'add_credential', 'delete_credential', 'view_credential',               # Credentials
        'add_exploit', 'delete_exploit', 'view_exploit',                        # Exploits
        'add_process', 'change_process', 'delete_process', 'view_process',      # Processes
        'add_step', 'change_step', 'delete_step', 'view_step',                  # Steps
        'view_tool',                                                            # Tools
        'view_intensity',                                                       # Intensities
        'view_configuration',                                                   # Configurations
        'view_input',                                                           # Inputs
        'view_output',                                                          # Outputs
        'add_wordlist', 'change_wordlist', 'delete_wordlist', 'view_wordlist'   # Wordlists
    ],
    Role.AUDITOR: [
        'view_project',                                                         # Projects
        'add_target', 'delete_target', 'view_target',                           # Targets
        'add_targetport', 'delete_targetport', 'view_targetport',               # Target ports
        'add_targetendpoint', 'delete_targetendpoint', 'view_targetendpoint',   # Target endpoints
        'add_task', 'delete_task', 'view_task',                                 # Tasks
        'view_execution',                                                       # Executions
        'add_osint', 'delete_osint', 'view_osint',                              # OSINT
        'add_host', 'delete_host', 'view_host',                                 # Hosts
        'add_enumeration', 'delete_enumeration', 'view_enumeration',            # Enumerations
        'add_endpoint', 'delete_endpoint', 'view_endpoint',                     # Endpoints
        'add_technology', 'delete_technology', 'view_technology',               # Technologies
        'add_vulnerability', 'change_vulnerability', 'delete_vulnerability', 'view_vulnerability',  # Vulnerabilities
        'add_credential', 'delete_credential', 'view_credential',               # Credentials
        'add_exploit', 'delete_exploit', 'view_exploit',                        # Exploits
        'add_process', 'change_process', 'delete_process', 'view_process',      # Processes
        'add_step', 'change_step', 'delete_step', 'view_step',                  # Steps
        'view_tool',                                                            # Tools
        'view_intensity',                                                       # Intensities
        'view_configuration',                                                   # Configurations
        'view_input',                                                           # Inputs
        'view_output',                                                          # Outputs
        'add_wordlist', 'change_wordlist', 'delete_wordlist', 'view_wordlist',  # Wordlists
    ],
    Role.READER: [
        'view_project',                                                         # Projects
        'view_target',                                                          # Targets
        'view_targetport',                                                      # Target ports
        'view_targetendpoint',                                                  # Target endpoints
        'view_task',                                                            # Tasks
        'view_execution',                                                       # Executions
        'view_osint',                                                           # OSINT
        'view_host',                                                            # Hosts
        'view_enumeration',                                                     # Enumerations
        'view_endpoint',                                                        # Endpoints
        'view_technology',                                                      # Technologies
        'view_vulnerability',                                                   # Vulnerabilities
        'view_credential',                                                      # Credentials
        'view_exploit',                                                         # Exploits
    ]
}
