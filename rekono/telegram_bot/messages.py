HELP_START = ''' To initialize Rekono Bot use the command: /start'''
HELP = ''' I'm working on it '''

WELCOME = '''
Welcome to Rekono Bot!

To start hacking, you must add the following token to your Rekono account: {start_token} 

After that, you can see the available commands typing /help

Enjoy!'''
LOGOUT = 'Bye!'

EXECUTION_NOTIFICATION = '''
{project}

Target: {target}
Task: {task}
Execution: {execution}
Tool: {tool}
Status: {status}
Start: {start}
End: {end}

{findings}
'''
FINDING_TITLE = '''
------------------------------
{finding}
------------------------------
'''
OSINT_ITEM = '''
Id: {id}
Data: {data}
Data type: {data_type}
Source: {source}
'''
HOST_ITEM = '''
Id: {id}
Address: {address}
OS: {os}
OS type: {os_type}
'''
ENUMERATION_ITEM = '''
Id: {id}
Host: {host_id}
Port: {port}
Port status: {port_status}
Protocol: {protocol}
Service: {service}
'''
TECHNOLOGY_ITEM = '''
Id: {id}
Enumeration: {enumeration_id}
Technology: {name}
Version: {version}
'''
ENDPOINT_ITEM = '''
Id: {id}
Enumeration: {enumeration_id}
Endpoint: {endpoint}
Status: {status}
'''
VULNERABILITY_ITEM = '''
Id: {id}
Enumeration: {enumeration_id}
Technology: {technology}
Name: {name}
Description: {description}
CVE: {cve}
Severity: {severity}
'''
CREDENTIAL_ITEM = '''
Id: {id}
Email: {email}
Username: {username}
Secret: {secret}
'''
EXPLOIT_ITEM = '''
Id: {id}
Vulnerability: {vulnerability_id}
Technology: {technology_id}
Name: {name}
'''
