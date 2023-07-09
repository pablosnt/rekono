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
        'add_task', 'delete_task', 'view_task',                                 # Tasks
        'view_execution',                                                       # Executions
        'add_osint', 'delete_osint', 'view_osint',                              # OSINT
        'add_host', 'delete_host', 'view_host',                                 # Hosts
        'add_port', 'delete_port', 'view_port',                                 # Ports
        'add_path', 'delete_path', 'view_path',                                 # Paths
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
        'view_system', 'change_system',                                         # System
    ],
    Role.AUDITOR: [
        'view_project',                                                         # Projects
        'add_target', 'delete_target', 'view_target',                           # Targets
        'add_targetport', 'delete_targetport', 'view_targetport',               # Target ports
        'add_task', 'delete_task', 'view_task',                                 # Tasks
        'view_execution',                                                       # Executions
        'add_osint', 'delete_osint', 'view_osint',                              # OSINT
        'add_host', 'delete_host', 'view_host',                                 # Hosts
        'add_port', 'delete_port', 'view_port',                                 # Ports
        'add_path', 'delete_path', 'view_path',                                 # Paths
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
        'view_system',                                                          # System
    ],
    Role.READER: [
        'view_project',                                                         # Projects
        'view_target',                                                          # Targets
        'view_targetport',                                                      # Target ports
        'view_task',                                                            # Tasks
        'view_execution',                                                       # Executions
        'view_osint',                                                           # OSINT
        'view_host',                                                            # Hosts
        'view_port',                                                            # Ports
        'view_path',                                                            # Paths
        'view_technology',                                                      # Technologies
        'view_vulnerability',                                                   # Vulnerabilities
        'view_credential',                                                      # Credentials
        'view_exploit',                                                         # Exploits
        'view_system',                                                          # System
    ]
}
