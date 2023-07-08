'''Messages with findings data for execution notification.'''

TITLE = '''
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

{icon} *{finding}*
'''

OSINT_ICON = '🗣'
OSINT = '''
_Data_          *{data}*
_Data type_     {data_type}
_Source_        {source}
'''

HOST_ICON = '🖥 '
HOST = '''
_Address_   *{address}*
_OS_        {os}
_OS type_   {os_type}
'''

PORT_ICON = '🚪'
PORT = '''
_Host_          *{host}*
_Port_          *{port}*
_Status_        {status}
_Protocol_      {protocol}
_Service_       {service}
'''
PORT_PARAM = '''
_Port_          *{port}*
'''

PATH_ICON = '🌐'
PATH = '''
_Port_          *{port}*
_Type_          {type}
_Path_          *{path}*
_Status_        {status}
_Extra_         {extra}
'''

TECHNOLOGY_ICON = '🖲'
TECHNOLOGY = '''
_Port_          *{port}*
_Name_          *{name}*
_Version_       {version}
'''
TECHNOLOGY_PARAM = '''
_Technology_    *{technology}*
'''

CREDENTIAL_ICON = '🔑'
CREDENTIAL = '''
_Email_     *{email}*
_Username_  *{username}*
_Secret_    *{secret}*
_Context_   *{context}*
'''

VULNERABILITY_ICON = '🐛'
VULNERABILITY = '''
_Name_              *{name}*
_Description_       {description}
_Severity_          {severity}
_CVE_               *{cve}*
_Reference_         {reference}
'''
VULNERABILITY_PARAM = '''
_Vulnerability_     *{vulnerability}*
'''

EXPLOIT_ICON = '🧨'
EXPLOIT = '''
_Title_          *{title}*
_Reference_     {reference}
'''
