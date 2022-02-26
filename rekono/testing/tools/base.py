import os
from typing import Any, Dict, List

from django.test import TestCase
from django.utils import timezone
from executions.models import Execution
from projects.models import Project
from targets.models import Target
from tasks.enums import Status
from tasks.models import Task
from tools.enums import IntensityRank
from tools.models import Configuration, Intensity, Tool
from tools.utils import get_tool_class_by_name


class ToolParserTest(TestCase):
    '''Base test case for tool parsers.'''

    tool_name = ''                                                              # Tool name to set by subclasses
    # Tool reports path
    reports_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'reports')

    def setUp(self) -> None:
        '''Create initial data before run tests.'''
        super().setUp()
        if self.tool_name:
            # Create a testing environment to be able to create a consistent execution object
            tool = Tool.objects.get(name=self.tool_name)
            configuration = Configuration.objects.get(tool=tool, default=True)
            intensity = Intensity.objects.filter(tool=tool).first()
            project = Project.objects.create(name='Test', description='Test', tags=['test'])
            target = Target.objects.create(project=project, target='10.10.10.10')
            task = Task.objects.create(
                target=target,
                tool=tool,
                configuration=configuration,
                intensity=IntensityRank.NORMAL,
                status=Status.COMPLETED,
                start=timezone.now(),
                end=timezone.now()
            )
            execution = Execution.objects.create(
                task=task,
                status=Status.COMPLETED,
                start=timezone.now(),
                end=timezone.now()
            )
            tool_class = get_tool_class_by_name(self.tool_name)                 # Get tool class from name
            self.tool = tool_class(execution, tool, configuration, intensity, [])   # Create tool instance

    def check_tool_parser(self, filename: str, expected: List[Dict[str, Any]]) -> None:
        '''Check expected findings for results obtained after parse tool report.

        Args:
            filename (str): Report filename to parse
            expected (List[Dict[str, Any]]): Expected findings data. Requires the field 'model' to check finding type
        '''
        self.tool.path_output = os.path.join(self.reports_path, self.tool_name.lower(), filename)   # Set report file
        self.tool.parse_output_file()                                           # Parse tool report
        self.assertEqual(len(expected), len(self.tool.findings))                # Check total number of findings
        for index, finding_data in enumerate(expected):                         # For each expected finding
            self.assertTrue(isinstance(self.tool.findings[index], finding_data.pop('model')))   # Check finding type
            for key, value in finding_data.items():                             # For each finding field
                self.assertEqual(value, getattr(self.tool.findings[index], key))    # Check finding value
