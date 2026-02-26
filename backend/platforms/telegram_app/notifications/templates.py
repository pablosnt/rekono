"""Telegram message templates for security notifications.

Defines message templates and formatting for Telegram Bot notifications
including execution reports, findings display, and alert formatting.
"""

from findings.models import OSINT, Credential, Exploit, Host, Path, Port, Technology, Vulnerability

EXECUTION = """
*{project}*

✅ _Status_            *{status}*
🎯 _Target_            *{target}*
🛠 _Tool_              *{tool}*
⚙️ _Configuration_      {configuration}
🔜 _Start_             {start}
🔚 _End_               {end}
👤 _Executor_          {executor}

{findings}
"""

HEADER = """
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

{icon} *{title}*

{details}
"""

FINDINGS = {
    OSINT: {
        "icon": "📖",
        "template": """
_Data_          *{data}*
_Data type_     {data_type}
_Source_        {source}
""",
    },
    Host: {
        "icon": "🖥",
        "template": """
_Address_   *{ip}*
_Domain_    {domain}
_OS_        {os}
_OS type_   {os_type}
_Country_   {country}
_City_      {city}
""",
    },
    Port: {
        "icon": "📥",
        "template": """
_Port_          *{port}*
_Service_       *{service}*
_Status_        {status}
_Protocol_      {protocol}
_Host_          {host}
""",
    },
    Path: {
        "icon": "🛣",
        "template": """
_Path_          *{path}*
_Type_          {type}
_Status_        {status}
_Port_          {port}
""",
    },
    Technology: {
        "icon": "🖲",
        "template": """
_Name_          *{name}*
_Version_       {version}
_Port_          {port}
""",
    },
    Credential: {
        "icon": "🔑",
        "template": """
_Email_         *{email}*
_Username_      *{username}*
_Secret_        *{secret}*
_Technology_    {technology}
_Context_       {context}
""",
    },
    Vulnerability: {
        "icon": "🐛",
        "template": """
_Name_              *{name}*
_CVE_               *{cve}*
_Severity_          *{severity}*
_CWE_               {cwe}
_Port_              {port}
_Technology_        {technology}
_Reference_         {reference}

{description}
""",
    },
    Exploit: {
        "icon": "💣",
        "template": """
_Title_             *{title}*
_Vulnerability_     {vulnerability}
_Technology_        {technology}
_Reference_         {reference}
""",
    },
}

ALERT_TRENDING_CVE = "[ALERT] New trending CVE 🔥"
ALERT = "[ALERT] New {finding} detected"
