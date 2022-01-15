from typing import List, Tuple

from defectdojo.api import DefectDojo
from defectdojo.exceptions import DefectDojoException
from executions.models import Execution
from findings.models import Endpoint, Finding
from projects.models import Project

from rekono.settings import DEFECT_DOJO

# Defect-Dojo client
dd_client = DefectDojo()


def get_product(project: Project) -> int:
    '''Get Defect-Dojo product Id from Rekono project, or create it if needed.

    Args:
        project (Project): Rekono project

    Raises:
        DefectDojoException: Raised if Defect-Dojo product is not found and can't be created

    Returns:
        int: Defect-Dojo product Id
    '''
    if project.defectdojo_product_id:                                           # Rekono project with product
        return project.defectdojo_product_id
    elif DEFECT_DOJO.get('PRODUCT_AUTO_CREATION'):                              # Defect-Dojo creation enabled
        product_type = None
        success, body = dd_client.get_rekono_product_type()                     # Get product type associated to Rekono
        if success and body and 'results' in body and len(body['results']) > 0:
            product_type = body['results'][0].get('id')
        else:                                                                   # Error obtaining product type
            # Create product type associated to Rekono
            success, body = dd_client.create_rekono_product_type()
            if success:
                product_type = body.get('id')
        if product_type:                                                        # If product type found or created
            success, body = dd_client.create_product(product_type, project)     # Create product associated to project
            if success:
                project.defectdojo_product_id = body['id']                      # Save the Id in the Rekono project
                project.save(update_fields=['defectdojo_product_id'])
                return body['id']
    raise DefectDojoException(f'Product associated to project {project.id} not found')


def get_engagement(project: Project, id: int, name: str, description: str) -> Tuple[int, int]:
    '''Get Defect-Dojo engagement Id for Rekono project, or create it if needed.

    Args:
        project (Project): Rekono project
        id (int): Engagement Id to get
        name (str): Name to use in the engagement creation
        description (str): Description to use in the engagement creation

    Raises:
        DefectDojoException: Raised if Defect-Dojo engagement is not found and can't be created

    Returns:
        int: Defect-Dojo engagement Id
    '''
    if id:                                                                      # Id provided
        success, body = dd_client.get_engagement(id)                            # Get engagement from Defect-Dojo
        if success and body:
            # Engagement product doesn't match the product associated to the Rekono project
            if project.defectdojo_product_id and project.defectdojo_product_id != body.get('id'):
                raise DefectDojoException(f'Invalid engagement Id {id} for project {project.id}')
            else:
                return project.defectdojo_product_id, body['id']
        raise DefectDojoException(f'Engagement Id {id} not found')              # Engagement not found in Defect-Dojo
    elif name and description:                                                  # Name and description provided
        product_id = get_product(project)                                       # Get Defect-Dojo product
        # Create a new engagement in Defect-Dojo
        success, body = dd_client.create_engagement(product_id, name, description)
        if success and body:
            return product_id, body['id']
    raise DefectDojoException('Invalid engagement')


def create_rekono_test(engagement_id: int) -> int:
    '''Create a new test associated to Rekono in a specific Defect-Dojo engagement.

    Args:
        engagement_id (int): Engagement Id where the test will be created

    Raises:
        DefectDojoException: Raised if the test can't be created

    Returns:
        int: Defect-Dojo test Id
    '''
    test_type = None
    result, body = dd_client.get_rekono_test_type()                             # Get Rekono test type
    if result and body and 'results' in body and len(body['results']) > 0:
        test_type = body['results'][0].get('id')
    else:                                                                       # Rekono test type not found
        result, body = dd_client.create_rekono_test_type()                      # Create Rekono test type
        if result:
            test_type = body.get('id')
    if test_type:                                                               # If test type found or created
        result, body = dd_client.create_rekono_test(test_type, engagement_id)   # Create Rekono test
        if result:
            return body['id']
    raise DefectDojoException('Unexpected error in Rekono test creation')       # Rekono test can't be created


def scans(
    project: Project,
    executions: List[Execution],
    engagement_id: int,
    name: str,
    description: str
) -> None:
    '''Import in Defect-Dojo the output of the provided executions.

    Args:
        project (Project): Rekono project associated to the executions
        executions (List[Execution]): Execution list whose output will be imported in Defect-Dojo
        engagement_id (int): Engagement Id where the scans will be imported
        name (str): Name to create a new engagement where the scans will be imported
        description (str): Description to create a new engagement where the scans will be imported
    '''
    # Get or create the engagement
    _, engagement_id = get_engagement(project, engagement_id, name, description)
    for execution in executions:                                                # For each execution
        tool = execution.step.tool if execution.step else execution.task.tool   # Get the associated tool
        # Check if tool is supported in Defect-Dojo:
        # https://defectdojo.github.io/django-DefectDojo/integrations/parsers/
        if tool.defectdojo_scan_type:
            success, _ = dd_client.import_scan(engagement_id, execution, tool)  # Import the execution output
            if success:
                execution.reported_to_defectdojo = True                         # Update the execution as reported
                execution.save(update_fields=['reported_to_defectdojo'])


def findings(
    project: Project,
    findings: List[Finding],
    engagement_id: int,
    name: str,
    description: str
) -> None:
    '''Import in Defect-Dojo a finding list.

    Args:
        project (Project): Rekono project associated to the findings
        findings (List[Finding]): Finding list whose output will be imported in Defect-Dojo
        engagement_id (int): Engagement Id where the findings will be imported
        name (str): Name to create a new engagement where the findings will be imported
        description (str): Description to create a new engagement where the findings will be imported

    Raises:
        DefectDojoException: Raised if Defect-Dojo test is not found and can't be created
    '''
    # Get or create the engagement
    product_id, engagement_id = get_engagement(project, engagement_id, name, description)
    test_id = None
    for finding in findings:                                                    # For each finding
        success = False
        if isinstance(finding, Endpoint):                                       # Endpoint finding
            if not product_id:
                product_id = get_product(project)                               # Get the product if not found before
            success, _ = dd_client.create_endpoint(product_id, finding)         # Import finding as Defect-Dojo endpoint
        else:
            if not test_id:
                test_id = create_rekono_test(engagement_id)                     # Create the test if not created before
            success, _ = dd_client.create_finding(test_id, finding)             # Import finding as Defect-Dojo finding
        if success:
            finding.reported_to_defectdojo = True                               # Update the finding as reported
            finding.save(update_fields=['reported_to_defectdojo'])
