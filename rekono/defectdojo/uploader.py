from defectdojo.api import engagements, products, scans
from defectdojo.exceptions import (EngagementIdNotFoundException,
                                   ProductIdNotFoundException)

from rekono.settings import DEFECT_DOJO as config


def upload_executions(executions: list) -> None:
    project = executions[0].task.target.project
    if not project.defectdojo_product_id and config.get('AUTO_CREATION'):
        project = products.create_new_product(project)
    if not project.defectdojo_product_id:
        raise ProductIdNotFoundException(
            f'Product ID associated to project {project.id} not found and can not be created'
        )
    engagement = engagements.get_rekono_engagement(project.defectdojo_product_id)
    if not engagement:
        raise EngagementIdNotFoundException(
            f'Rekono engagement not found and can not be created for product ID {project.defectdojo_product_id}'    # noqa: E501
        )
    for execution in executions:
        tool = execution.step.tool if execution.step else execution.task.tool
        if not tool.defectdojo_scan_type:
            continue
        scans.import_scan(engagement, execution, tool)
