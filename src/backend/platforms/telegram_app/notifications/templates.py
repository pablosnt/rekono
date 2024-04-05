from alerts.enums import AlertMode
from findings.models import (
    OSINT,
    Credential,
    Exploit,
    Host,
    Path,
    Port,
    Technology,
    Vulnerability,
)

EXECUTION = """
*{project}*

🎯 _Target_            *{target}*
🛠 _Tool_              *{tool}*
⚙️ _Configuration_      {configuration}
✅ _Status_            *{status}*
🔜 _Start_             {start}
🔚 _End_               {end}
👤 _Executor_          {executor}

{findings}
"""

HEADER = """
\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

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
_Address_   *{address}*
_OS_        {os}
_OS type_   {os_type}
""",
    },
    Port: {
        "icon": "📥",
        "template": """
_Host_          {host}
_Port_          *{port}*
_Status_        {status}
_Protocol_      {protocol}
_Service_       *{service}*
""",
    },
    Path: {
        "icon": "🛣",
        "template": """
_Port_          {port}
_Type_          {type}
_Path_          *{path}*
_Status_        {status}
_Extra_         {extra_info}
""",
    },
    Technology: {
        "icon": "🖲",
        "template": """
_Port_          {port}
_Name_          *{name}*
_Version_       {version}
""",
    },
    Credential: {
        "icon": "🔑",
        "template": """
_Email_         *{email}*
_Username_      *{username}*
_Secret_        *{secret}*
_Context_       {context}
""",
    },
    Vulnerability: {
        "icon": "🐛",
        "template": """
_Port_              {port}
_Technology_        {technology}
_Name_              *{name}*
_Description_       {description}
_Severity_          {severity}
_CVE_               *{cve}*
_Reference_         {reference}
""",
    },
    Exploit: {
        "icon": "💣",
        "template": """
_Vulnerability_     {vulnerability}
_Technology_        {technology}
_Title_             *{title}*
_Reference_         {reference}
""",
    },
}

ALERTS = {
    AlertMode.NEW.value: "[ALERT] New {finding} detected",
    AlertMode.FILTER.value: "[ALERT] New {finding} matches the criteria",
    AlertMode.MONITOR.value: "[ALERT] New trending CVE 🔥",
}
