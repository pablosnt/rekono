from defectdojo.api import DefectDojo
from defectdojo.exceptions import DefectDojoException
from findings.models import Endpoint
from projects.models import Project

from rekono.settings import DEFECT_DOJO

dd_client = DefectDojo()


def get_product(project: Project) -> int:
    if project.defectdojo_product_id:
        return project.defectdojo_product_id
    elif DEFECT_DOJO.get('PRODUCT_AUTO_CREATION'):
        product_type = None
        success, body = dd_client.get_rekono_product_type()
        if success and body and len(body.get('results')) > 0:
            product_type = body.get('results')[0].get('id')
        else:
            success, body = dd_client.create_rekono_product_type()
            if success:
                product_type = body.get('id')
        if product_type:
            success, body = dd_client.create_product(product_type, project)
            if success:
                project.defectdojo_product_id = body.get('id')
                project.save(update_fields=['defectdojo_product_id'])
                return body.get('id')
    raise DefectDojoException(f'Product associated to project {project.id} not found')


def get_engagement(project: Project, id: int, name: str, description: str) -> int:
    if id:
        success, body = dd_client.get_engagement(id)
        if success and body:
            if project.defectdojo_product_id and project.defectdojo_product_id != body.get('id'):
                raise DefectDojoException(f'Invalid engagement Id {id} for project {project.id}')
            else:
                return project.defectdojo_product_id, body.get('id')
        raise DefectDojoException(f'Engagement Id {id} not found')
    elif name and description:
        product_id = get_product(project)
        success, body = dd_client.create_engagement(product_id, name, description)
        if success and body:
            return product_id, body.get('id')
        raise DefectDojoException('Invalid engagement')


def scans(
    project: Project,
    executions: list,
    engagement_id: int,
    name: str,
    description: str
) -> None:
    _, engagement_id = get_engagement(project, engagement_id, name, description)
    for execution in executions:
        tool = execution.step.tool if execution.step else execution.task.tool
        if tool.defectdojo_scan_type:
            success, _ = dd_client.import_scan(engagement_id, execution, tool)
            if success:
                execution.reported_to_defectdojo = True
                execution.save(update_fields=['reported_to_defectdojo'])


def findings(
    project: Project,
    findings: list,
    engagement_id: int,
    name: str,
    description: str
) -> None:
    product_id, engagement_id = get_engagement(project, engagement_id, name, description)
    test_id = None
    for finding in findings:
        success = False
        if isinstance(finding, Endpoint):
            if not product_id:
                product_id = get_product(project)
            success, _ = dd_client.create_endpoint(product_id, finding)
        else:
            if not test_id:
                test_type = None
                result, body = dd_client.get_rekono_product_type()
                if result and body and len(body.get('results')) > 0:
                    test_type = body.get('results')[0].get('id')
                else:
                    result, body = dd_client.create_rekono_product_type()
                    if result:
                        test_type = body.get('id')
                if test_type:
                    result, body = dd_client.create_rekono_test(test_type, engagement_id)
                    if result:
                        test_id = body.get('id')
                if not test_id:
                    raise DefectDojoException('Unexpected error in Rekono test creation')
            success, _ = dd_client.create_finding(test_id, finding)
        if success:
            finding.reported_to_defectdojo = True
            finding.save(update_fields=['reported_to_defectdojo'])
