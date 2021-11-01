from typing import Any

from defectdojo.api import engagements, findings, products, scans, tests
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                   InvalidEngagementIdException,
                                   ProductIdNotFoundException)
from findings.models import Endpoint

from rekono.settings import DEFECT_DOJO as config


def get_product_id(project: Any) -> int:
    if not project.defectdojo_product_id and config.get('PROD_AUTO_CREATION'):
        product_id = products.create_new_product(project)
        if product_id:
            project.defectdojo_product_id = product_id
            project.save()
            return product_id
    elif project.defectdojo_product_id:
        return project.defectdojo_product_id
    raise ProductIdNotFoundException(
        f'Product ID associated to project {project.id} not found and can not be created'
    )


def get_engagement_id(
    project: Any,
    engagement_id: int = None,
    engagement_name: str = None,
    engagement_description: str = None
):
    if engagement_id:
        prod_id, eng_id = engagements.check_engagement(engagement_id, project.defectdojo_product_id)
        if eng_id:
            project.defectdojo_product_id = prod_id
            project.save()
            return prod_id, eng_id
        if project.defectdojo_product_id and not eng_id:
            raise InvalidEngagementIdException(
                f'Engagement {engagement_id} not found for product {project.defectdojo_product_id}'
            )
        else:
            raise EngagementIdNotFoundException(f'Engagement {engagement_id} not found')
    elif engagement_name and engagement_description:
        prod_id = get_product_id(project)
        eng_id = engagements.get_last_engagement(prod_id, engagement_name)
        if not eng_id:
            eng_id = engagements.create_new_engagement(
                prod_id,
                engagement_name,
                engagement_description
            )
        return prod_id, eng_id


def upload_executions(
    rekono_executions: list,
    engagement_id: int = None,
    engagement_name: str = None,
    engagement_description: str = None
) -> None:
    _, engagement = get_engagement_id(
        rekono_executions[0].task.target.project,
        engagement_id,
        engagement_name,
        engagement_description
    )
    for execution in rekono_executions:
        tool = execution.step.tool if execution.step else execution.task.tool
        if tool.defectdojo_scan_type:
            scans.import_scan(engagement, execution, tool)


def upload_findings(
    rekono_findings: list,
    engagement_id: int = None,
    engagement_name: str = None,
    engagement_description: str = None
) -> None:
    product, engagement = get_engagement_id(
        rekono_findings[0].execution.task.target.project,
        engagement_id,
        engagement_name,
        engagement_description
    )
    test = tests.create_rekono_test(engagement)
    for finding in rekono_findings:
        if isinstance(finding, Endpoint):
            findings.create_endpoint(product, finding)
        else:
            findings.create_finding(test, finding)
