import logging
import os
import re
import shutil
import subprocess
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from authentications.models import Authentication
from django.db.models import Model
from django.db.models.fields.related_descriptors import \
    ReverseManyToOneDescriptor
from django.db.models.query_utils import DeferredAttribute
from django.utils import timezone
from executions.models import Execution
from findings.models import Finding, Port, Vulnerability
from findings.queue import producer
from findings.utils import get_unique_filter
from input_types.base import BaseInput
from targets.models import TargetPort
from tasks.enums import Status
from tools.exceptions import ToolExecutionException
from tools.models import Argument, Input, Intensity

from rekono.settings import REPORTS_DIR, TESTING

logger = logging.getLogger()                                                    # Rekono logger


class BaseTool:
    '''Parent class for all tools that creates the command, executes it and sends findings to the findings queue.'''

    # Indicate if execution must continue even if error occurs during tool execution. By default False.
    ignore_exit_code = False
    script = ''                                                                 # Indicate the script path to execute

    def __init__(self, execution: Execution, intensity: Intensity, arguments: List[Argument]) -> None:
        '''Tool constructor.

        Args:
            execution (Execution): Execution entity related to the tool execution
            intensity (Intensity): Intensity to apply
            arguments (List[Argument]): Arguments implicated in the tool execution
        '''
        self.execution = execution
        self.tool = execution.tool
        self.configuration = execution.configuration
        self.intensity = intensity
        self.arguments = arguments
        self.command_arguments: List[str] = []                                  # Arguments used for execute tool
        self.file_output_enabled = self.tool.output_format is not None          # Tool output to file enabled
        self.file_output_extension = self.tool.output_format or 'txt'           # Tool output file extension
        self.filename_output = f'{str(uuid.uuid4())}.{self.file_output_extension}'  # Tool output file name
        self.path_output = os.path.join(REPORTS_DIR, self.filename_output)      # Tool output file path
        self.findings: List[Finding] = []                                       # Findings obtained from tool execution
        # Inputs used during tool execution
        # This data will be used to maintain relations between findings and previous findings always as possible
        self.findings_relations: Dict[str, BaseInput] = {}

    def check_installation(self) -> None:
        '''Check if tool is installed in the system.

        Raises:
            ToolExecutionException: Raised if tool isn't installed
        '''
        if (
            (self.tool.command and shutil.which(self.tool.command) is None) or  # Check command installation
            (self.script and not os.path.isfile(self.script))                   # Check if script exists
        ):
            raise ToolExecutionException(f'Tool {self.tool.name} is not installed in the system')

    def prepare_environment(self) -> None:
        '''Run code before tool execution. It can be implemented by child tool classes if needed.'''
        pass

    def clean_environment(self) -> None:
        '''Run code after tool execution. It can be implemented by child tool classes if needed.'''
        pass

    def format(self, argument: str, data: Dict[str, Any]) -> Union[str, None]:
        '''Format tool argument using data.

        Args:
            argument (str): Tool argument to be formatted
            data (Dict[str, Any]): Data to use in the tool argument

        Returns:
            Union[str, None]: Formatted argument
        '''
        data = {k: v for k, v in data.items() if v}                             # Clean input data
        try:
            return argument.format(**data)                                      # Build tool argument using inputs data
        except KeyError:
            return None                                                         # Inputs data isn't enough

    def format_argument(self, argument: str, base_inputs: List[BaseInput]) -> Union[str, None]:
        '''Format tool argument using multiple input objects.

        Args:
            argument (str): Tool argument to be formatted
            base_inputs (List[BaseInput]): Input objects to use in the tool argument

        Returns:
            Union[str, None]: Formatted argument
        '''
        data: Dict[str, Any] = {}                                               # Variable to store inputs data
        for base_input in base_inputs:                                          # For each input
            data = base_input.parse(data)                                       # Get input data
        return self.format(argument, data)

    def process_source(
        self,
        argument: Argument,
        input: Input,
        model: Model,
        source: List[BaseInput],
        command: Dict[str, str]
    ) -> Tuple[bool, Dict[str, str]]:
        '''Process a list of base inputs to include a new argument in the tool command.

        Args:
            argument (Argument): Tool argument
            input (Input): Argument input
            model (Model): Model associated to the tool input (can be the related model or the callback target)
            source (List[BaseInput]): List of base inputs to use in the tool argument
            command (Tuple[bool, Dict[str, str]]): Tool command created with previous arguments

        Returns:
            Tuple[bool, Dict[str, str]]: Boolean that indicates if some base input is found and the tool command updated
        '''
        # Indicate if finding or target is found for this argument input
        found = False
        # List of base inputs to include a multiple argument
        selection: List[BaseInput] = []
        for base_input in source:                                               # For each base input
            # Check base input model
            if not isinstance(base_input, model):
                continue
            found = True
            if not base_input.filter(input):                                    # Check input filter
                continue
            if argument.multiple:                                               # Multiple argument
                selection.append(base_input)                                    # Add base input to the selection
            else:                                                               # Unique argument
                # Format argument using current base input
                formatted_argument = self.format_argument(argument.argument, [base_input])
                if formatted_argument:                                          # If formatted argument is valid
                    command[argument.name] = formatted_argument                 # Add formatted argument to the command
                    # Save base input in the findings_relations to link findings later
                    self.findings_relations[model.__name__.lower()] = base_input
                    return found, command
        if selection:                                                           # If base input selection is not empty
            # Format argument using selected base inputs
            formatted_argument = self.format_argument(argument.argument, selection)
            if formatted_argument:                                              # If formatted argument is valid
                command[argument.name] = formatted_argument                     # Add formatted argument to the command
        return found, command

    def process_argument(
        self,
        argument: Argument,
        model_method: str,
        source: List[BaseInput],
        command: Dict[str, str]
    ) -> Tuple[bool, Dict[str, str]]:
        '''Process argument entity to include required base inputs in the tool command.

        Args:
            argument (Argument): Tool argument
            model_method (str): Method to get model from argument inputs
            source (List[BaseInput]): List of base inputs to use in the tool argument
            command (Dict[str, str]): Tool command created with previous arguments

        Returns:
            Tuple[bool, Dict[str, str]]: Boolean that indicates if some base input is found and the tool command updated
        '''
        found = False
        if argument.name not in command or not command[argument.name]:          # Argument can't be added yet
            for input in argument.inputs.order_by('order'):                     # For each argument input (ordered)
                model = getattr(input.type, model_method)()                     # Get model from input
                if model:                                                       # Model found
                    # Process base inputs
                    found, command = self.process_source(argument, input, model, source, command)
                    if found:                                                   # Related base input found and processed
                        break
        return found, command

    def get_authentication(
        self,
        targets_list: List[BaseInput],
        findings_list: List[Finding]
    ) -> Optional[Authentication]:
        '''Get authentication for a given list of targets and findings.

        Args:
            targets_list (List[BaseInput]): Targets list
            findings_list (List[Finding]): Findings list

        Returns:
            Optional[Authentication]: Authentication entity if found
        '''
        for ports in [
            [p for p in findings_list if isinstance(p, Port)],                  # Get Ports from findings list
            [p for p in targets_list if isinstance(p, TargetPort)],             # Get TargetPorts from targets list
        ]:
            if len(ports) > 0:                                                  # Ports found
                if len(ports) == 1:                                             # Only one port
                    authentications = Authentication.objects.filter(            # Look for authentication entity
                        target_port__target=self.execution.task.target,
                        target_port__port=cast(Union[Port, TargetPort], ports[0]).port
                    )
                    if authentications.exists():                                # Authentication found
                        return authentications.first()
                break
        return None

    def get_arguments(self, targets: List[BaseInput], previous_findings: List[Finding]) -> List[str]:
        '''Get tool arguments for the tool command.

        Args:
            targets (List[BaseInput]): List of targets and resources that can be included in the tool arguments
            previous_findings (List[Finding]): List of previous findings that can be included in the tool arguments

        Raises:
            ToolExecutionException: Raised if targets and previous findings aren't enough to build the arguments

        Returns:
            List[str]: List of tool arguments to use in the tool execution
        '''
        command = {
            'script': self.script,                                              # Script to execute the tool
            'command': self.tool.command,                                       # Add tool command to the arguments
            'intensity': self.intensity.argument,                               # Add intensity config to the arguments
            'output': self.path_output if self.file_output_enabled else ''      # Add output config to the arguments
        }
        authentication = self.get_authentication(targets, previous_findings)    # Search related authentication instance
        if authentication:                                                      # Authentication exists
            previous_findings.append(authentication)                            # Add authentication instance
        for argument in self.arguments:                                         # For each tool argument
            found, command = self.process_argument(
                argument,
                'get_model_class',
                cast(List[BaseInput], previous_findings),
                command
            )
            if not found:
                _, command = self.process_argument(argument, 'get_callback_model_class', targets, command)
            if argument.name not in command or not command[argument.name]:      # Argument can't be added
                if argument.required:                                           # Argument is required for the tool
                    raise ToolExecutionException(f'Tool configuration requires {argument.name} argument')
                else:                                                           # Argument is optional for the tool
                    command[argument.name] = ''                                 # Ignore this argument
        # Format configuration arguments with the built tool arguments
        args = self.configuration.arguments.format(**command)
        # Split arguments by whitespaces taking into account the arguments between quotes
        return [a.replace('"', '') for a in re.findall(r'[^\s\'"]*[\'"][^\'"]+[\'"]|[^\'"\s]+', args)]

    def check_arguments(self, targets: List[BaseInput], findings: List[Finding]) -> bool:
        '''Check if given resources (targets, resources and findings) lists are enough to execute the tool.

        Args:
            tool (BaseTool): Tool instance to be executed
            targets (List[BaseInput]): Target list (targets and resources) to include in the tool arguments
            findings (List[Finding]): Finding list to include in the tool arguments

        Returns:
            bool: Indicate if the tool can be executed with the given targets and findings
        '''
        try:
            self.get_arguments(targets, findings)                               # Try to configure the tool arguments
            return True
        except ToolExecutionException:
            return False

    def get_host_from_url(self, argument: str) -> str:
        '''Get host from URL used for tool execution.

        Args:
            argument (str): URL argument name

        Returns:
            str: Host associated to the URL
        '''
        index = self.command_arguments.index(argument) + 1
        host = self.command_arguments[index]
        if '://' in host:                                                       # URL with protocol data
            host = host.split('://', 1)[1]                                      # Remove protocol data from URL
        if host[-1] == '/':                                                     # URL ends in slash
            host = host[:-1]                                                    # Remove last slash form URL
        return host

    def get_environment(self, arguments: List[str]) -> Tuple[List[str], Dict[str, Any]]:
        '''Get environment variables from tool arguments.

        Args:
            arguments (List[str]): Tool arguments list

        Returns:
            Tuple[List[str], Dict[str, Any]]: Updated tool arguments to use and environment variables to apply
        '''
        environment = os.environ.copy()                                         # Copy current environment
        if self.tool.command not in arguments:
            arguments.insert(0, self.tool.command)                              # Combine tool command with arguments
        else:
            index = arguments.index(self.tool.command)                          # Get command index
            for definition in arguments[:index]:                                # For each previous argument
                if '=' not in definition:                                       # It isn't an environment variable
                    continue
                variable, value = definition.split('=', 1)                      # Parse variable
                environment[variable] = value.strip().replace('\'', '').replace('"', '')    # Add environment variable
            arguments = arguments[index:]                                       # Remove environment variable from args
        return arguments, environment

    def tool_execution(self, arguments: List[str]) -> str:
        '''Execute the tool.

        Args:
            arguments (List[str]): Arguments to include in the tool command

        Raises:
            ToolExecutionException: Raised if tool execution finishes with an exit code distinct than zero

        Returns:
            str: Plain output of the tool execution
        '''
        arguments, environment = self.get_environment(arguments)                # Get environment from argument
        logger.info(f'[Tool] Running: {" ".join(arguments)}')
        if hasattr(self, 'run_directory'):
            process = subprocess.run(                                           # Execute the tool in directory
                arguments,
                capture_output=True,
                env=environment,
                cwd=getattr(self, 'run_directory')
            )
        else:
            process = subprocess.run(arguments, capture_output=True, env=environment)   # Execute the tool
        if not self.ignore_exit_code and process.returncode > 0:
            # Execution error and ignore exit code is False
            raise ToolExecutionException(process.stderr.decode('utf-8'))
        return process.stdout.decode('utf-8')

    def create_finding(self, finding_type: Model, **fields: Any) -> Finding:
        '''Create finding from fields.

        Args:
            finding_type (Model): Finding model

        Returns:
            Finding: Created finding entity
        '''
        # Get unique filter for this finding model and from this fields
        unique_filter = get_unique_filter(finding_type.key_fields, fields, self.execution.task.target)
        finding = finding_type.objects.filter(**unique_filter).first()          # Check if finding already exists
        fields.update({
            'detected_by': self.tool,
            'last_seen': timezone.now(),
        })
        if finding:
            updated_fields = []
            for field, value in fields.items():                                 # For each finding field
                if value and value != getattr(finding, field):                  # Distinct value than the existing one
                    setattr(finding, field, value)                              # Update existing field
                    updated_fields.append(field)
            if updated_fields:
                finding.save(update_fields=updated_fields)                      # Update existing finding
        else:                                                                   # Finding not found
            finding = finding_type.objects.create(**fields)                     # Create new finding
        finding.executions.add(self.execution)                                  # Link finding to the current execution
        self.findings.append(finding)
        return finding

    def parse_output_file(self) -> None:
        '''Parse tool output file to create finding entities. This should be implemented by child tool classes.'''
        pass                                                                    # pragma: no cover

    def parse_plain_output(self, output: str) -> None:
        '''Parse tool plain output to create finding entities. This should be implemented by child tool classes.

        Args:
            output (str): Plain tool output
        '''
        pass                                                                    # pragma: no cover

    def process_findings(self) -> None:
        '''Set relations between parsed findings and previous findings, and send new findings to the findings queue.'''
        for finding in self.findings:                                           # For each parsed finding
            if (
                # Vulnerability with port and technology exists in saved relations
                isinstance(finding, Vulnerability) and
                getattr(finding, 'port') and
                'technology' in self.findings_relations
            ):
                # Remove port value because technology is more relevant
                setattr(finding, 'port', None)
                finding.save(update_fields=['port'])
            for key, value in self.findings_relations.items():                  # For each saved relations
                # Vulnerability with technology value and the current relation is with port
                if isinstance(finding, Vulnerability) and getattr(finding, 'technology') and key == 'port':
                    # Ignore this relation because technology relation is more relevant
                    continue
                if (
                    hasattr(finding, key) and
                    # Discard relations between findings
                    not isinstance(getattr(finding.__class__, key), ReverseManyToOneDescriptor) and
                    # Discard standard fields: Text, Number, etc.
                    not isinstance(getattr(finding.__class__, key), DeferredAttribute)
                ):
                    # Finding has a field that matches the current relation
                    setattr(finding, key, value)                                # Set relation between findings
                    finding.save(update_fields=[key])
        producer(self.execution, self.findings)                                 # Send findings to the findings queue

    def on_start(self) -> None:
        '''Perform changes in Execution entity when tool execution starts.'''
        self.execution.start = timezone.now()                                   # Set execution start date
        self.execution.save(update_fields=['start'])

    def on_skipped(self, message: str = None) -> None:
        '''Perform changes in Execution entity when tool execution is skipped.

        Args:
            message (str, optional): Descriptive message about the execution skipping
        '''
        self.execution.status = Status.SKIPPED                                  # Set execution status to Skipped
        self.execution.output_plain = message
        self.execution.end = timezone.now()                                     # Set execution end date
        self.execution.save(update_fields=['status', 'end', 'output_plain'])

    def on_running(self) -> None:
        '''Perform changes in Execution entity when command execution starts.'''
        self.execution.status = Status.RUNNING                                  # Set execution status to Running
        self.execution.save(update_fields=['status'])

    def on_error(self, stderr: str = None) -> None:
        '''Perform changes in Execution entity when command execution ends with errors.

        Args:
            stderr (str, optional): Command execution stderr. Defaults to None.
        '''
        if stderr:
            if self.path_output in stderr:
                stderr.replace(self.path_output, f'output.{self.tool.output_format}')   # Prevent information exposure
            self.execution.output_error = stderr.strip()                        # Save execution error output
        self.execution.status = Status.ERROR                                    # Set execution status to Error
        self.execution.end = timezone.now()                                     # Set execution end date
        self.execution.save(update_fields=['output_error', 'status', 'end'])

    def on_completed(self, stdout: str) -> None:
        '''Perform changes in Execution entity when command execution ends successfully.

        Args:
            stdout (str): Command execution stdout
        '''
        self.execution.status = Status.COMPLETED                                # Set execution status to Completed
        self.execution.end = timezone.now()                                     # Set execution end date
        if self.file_output_enabled and os.path.isfile(self.path_output):       # If tool execution has an output file
            self.execution.output_file = self.path_output.strip()               # Save output file path
        if self.path_output in stdout:
            stdout.replace(self.path_output, f'output.{self.tool.output_format}')   # Prevent information exposure
        self.execution.output_plain = stdout                                    # Save plain output
        self.execution.save(update_fields=['status', 'end', 'output_file', 'output_plain'])

    def run(self, targets: List[BaseInput], previous_findings: List[Finding]) -> None:
        '''Run tool.

        Args:
            targets (List[BaseInput]): List of targets and resources
            previous_findings (List[Finding]): List of previous findings
        '''
        self.on_start()                                                         # Start execution
        try:
            self.check_installation()                                           # Check tool installation
        except ToolExecutionException as ex:                                    # Tool installation not found
            logger.error(f'[Tool] Tool {self.tool.name} is not installed in the system. This execution will be skipped')
            self.on_skipped(str(ex))                                            # Skip execution
            return
        try:
            # Get arguments to include in command
            self.command_arguments = self.get_arguments(targets, previous_findings)
        except ToolExecutionException as ex:
            logger.error(f'[Tool] {str(ex)}')
            # Targets and findings aren't enough to build the command
            self.on_skipped(str(ex))                                            # Skip execution
            return
        self.prepare_environment()                                              # Prepare environment
        self.on_running()                                                       # Run execution
        try:
            output = ''
            if not TESTING:
                # Run tool
                output = self.tool_execution(self.command_arguments)            # pragma: no cover
        except ToolExecutionException as ex:                                    # pragma: no cover
            logger.error(f'[Tool] {self.tool.name} execution finish with errors')
            # Error during tool execution
            self.on_error(stderr=str(ex))                                       # Execution error
            self.clean_environment()                                            # Clean environment
            return
        except Exception as ex:                                                 # pragma: no cover
            logger.error(f'[Tool] Unexpected error during {self.tool.name} execution')
            logger.error(str(ex))
            # Unexpected error during tool execution
            self.on_error()                                                     # Execution error
            self.clean_environment()                                            # Clean environment
            return
        self.clean_environment()                                                # Clean environment
        self.on_completed(output)                                               # Completed execution
        logger.info(f'[Tool] {self.tool.name} execution has been completed')
        if self.file_output_enabled and os.path.isfile(self.path_output) and os.stat(self.path_output).st_size > 0:
            # Output file exists
            self.parse_output_file()                                            # Parse output file
        else:                                                                   # Output file not found
            self.parse_plain_output(output)                                     # Parse plain output
        logger.info(f'[Tool] {len(self.findings)} findings parsed from {self.tool.name} output')
        self.process_findings()                                                 # Process parsed findings
