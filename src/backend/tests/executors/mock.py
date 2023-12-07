from typing import Any


def get_url(*args: Any, **kwargs: Any) -> str:
    url = f"http://{args[1]}"
    if len(args) > 2:
        url += f":{args[2]}"
    url += args[3] if len(args) > 3 else "/"
    return url
