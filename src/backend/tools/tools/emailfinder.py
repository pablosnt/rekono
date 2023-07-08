from django.core.exceptions import ValidationError
from django.forms import EmailField
from findings.enums import DataType
from findings.models import OSINT
from tools.tools.base_tool import BaseTool


class Emailfinder(BaseTool):
    '''EmailFinder tool class.'''

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        checker = EmailField()
        for line in output.split('\n'):                                         # Get output by lines
            if line.strip():
                try:
                    checker.clean(line.strip())                                 # Check email value
                    self.create_finding(OSINT, data=line.strip(), data_type=DataType.EMAIL)
                except ValidationError:
                    pass
