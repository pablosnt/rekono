from typing import Any, Dict


def return_true(*args: Any) -> bool:
    return True


def create_product_type(*args: Any) -> Dict[str, Any]:
    return {"id": 1, "name": args[1], "description": args[2]}


def create_product(*args: Any) -> Dict[str, Any]:
    return {
        "id": 1,
        "prod_type": args[1],
        "name": args[2],
        "description": args[3],
        "tags": args[4],
    }


def create_engagement(*args: Any) -> Dict[str, Any]:
    return {
        "id": 1,
        "product": args[1],
        "name": args[2],
        "description": args[3],
        "tags": args[4],
    }


def return_defectdojo_data(field: str, **kwargs: Any) -> Dict[str, Any]:
    return {"id": 1, **kwargs.get(field).defect_dojo()}


def create_endpoint(**kwargs: Any) -> Dict[str, Any]:
    return return_defectdojo_data("endpoint", **kwargs)


def create_finding(**kwargs: Any) -> Dict[str, Any]:
    return return_defectdojo_data("finding", **kwargs)


def import_scan(*args: Any) -> Dict[str, Any]:
    return {
        "test_id": 1,
        "engagement_id": 1,
        "product_id": 1,
        "product_type_id": 1,
        "active": True,
    }
