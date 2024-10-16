from typing import Any


def return_true(*args: Any) -> bool:
    return True


def return_false(*args: Any) -> bool:
    return False


def return_id(*args: Any) -> dict[str, int]:
    return {"id": 1}


def create_product_type(*args: Any) -> dict[str, Any]:
    return {"id": 1, "name": args[1], "description": args[2]}


def create_product(*args: Any) -> dict[str, Any]:
    return {
        "id": 1,
        "prod_type": args[1],
        "name": args[2],
        "description": args[3],
        "tags": args[4],
    }


def create_engagement(*args: Any) -> dict[str, Any]:
    return {
        "id": 1,
        "product": args[1],
        "name": args[2],
        "description": args[3],
        "tags": args[4],
    }


def create_test_type(*args: Any) -> dict[str, Any]:
    return {"id": 1, "name": args[1], "tags": args[2], "dynamic_tool": True}


def create_test(*args: Any) -> dict[str, Any]:
    return {
        "id": 1,
        "test_type": args[1],
        "engagement": args[2],
        "title": args[3],
        "description": args[4],
    }


def import_scan(*args: Any) -> dict[str, Any]:
    return {
        "test_id": 1,
        "engagement_id": 1,
        "product_id": 1,
        "product_type_id": 1,
        "active": True,
    }
