import logging
from typing import List, Tuple

from defectdojo.api import DefectDojo
from defectdojo.exceptions import DefectDojoException
from executions.models import Execution
from findings.models import Finding, Path
from projects.models import Project
from targets.models import Target

dd_client = DefectDojo()                                                        # Defect-Dojo client

logger = logging.getLogger()                                                    # Rekono logger


def get_product_and_engagement_id(project: Project, target: Target) -> Tuple[int, int]:
    '''Get product Id and engagement Id to use to Defect-Dojo import.

    Args:
        project (Project): Rekono project
        target (Target): Rekono target

    Returns:
        Tuple[int, int]: Defect-Dojo product Id and engagement Id
    '''
    product_id = project.defectdojo_product_id
    to_check = [(dd_client.get_product, product_id, 'product')]
    engagement_id = project.defectdojo_engagement_id
    if project.defectdojo_engagement_by_target:
        engagement_id = target.get_defectdojo_engagement(dd_client)
    else:
        to_check.append((dd_client.get_engagement, engagement_id, 'engagement'))
    for checker, id, name in to_check:
        check, _ = checker(id)
        if not check:
            raise DefectDojoException({name.lower(): [f'{name.capitalize()} {id} is not found in Defect-Dojo']})
    return product_id, engagement_id


def get_rekono_test(engagement_id: int) -> int:
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
    if result and body and len(body.get('results', [])) > 0:
        test_type = body['results'][0].get('id')
    else:                                                                       # Rekono test type not found
        result, body = dd_client.create_rekono_test_type()                      # Create Rekono test type
        if result:
            logger.info(f'[Defect-Dojo] Rekono test type {body["id"]} has been created')
            test_type = body.get('id')
    if test_type:                                                               # If test type found or created
        result, body = dd_client.create_rekono_test(test_type, engagement_id)   # Create Rekono test
        if result:
            logger.info(f'[Defect-Dojo] Rekono test {body["id"]} has been created')
            return body['id']
    logger.warning("[Defect-Dojo] Rekono test can't be created")
    raise DefectDojoException({'test': ['Unexpected error in Rekono test creation']})   # Rekono test can't be created


def report(execution: Execution, findings: List[Finding]) -> None:
    '''Report to Defect-Dojo the results of one Rekono execution.

    Args:
        execution (Execution): Execution to be reported
        findings (List[Finding]): Findings detected during the execution

    Raises:
        DefectDojoException: Raised if Defect-Dojo is not available
    '''
    if not dd_client.is_available():
        raise DefectDojoException({'defect-dojo': ['Integration with Defect-Dojo is not available']})
    product_id, engagement_id = get_product_and_engagement_id(execution.task.target.project, execution.task.target)
    if execution.tool.defectdojo_scan_type:
        dd_client.import_scan(engagement_id, execution)                         # Import the execution output
        logger.info(f'[Defect-Dojo] Execution {execution.id} has been imported in engagement {engagement_id}')
    else:
        test_id = None
        for finding in findings:
            if isinstance(finding, Path):                                       # Path finding
                dd_client.create_endpoint(product_id, finding)                  # Import finding as Defect-Dojo endpoint
            else:
                test_id = test_id if test_id else get_rekono_test(engagement_id)
                dd_client.create_finding(test_id, finding)                      # Import finding as Defect-Dojo finding
            logger.info(
                f'[Defect-Dojo] {finding.__class__.__name__} {finding.id} has been imported in product {product_id}'
            )
    execution.imported_in_defectdojo = True                                     # Update the execution as reported
    execution.save(update_fields=['imported_in_defectdojo'])
