from typing import Any

from settings.models import Settings
from tests.cases import ApiTestCase
from tests.framework import ApiTest
from wordlists.enums import WordlistType
from wordlists.models import Wordlist

# pytype: disable=wrong-arg-types

# Wordlists paths
data_dir = ApiTest.data_dir / "wordlists"
endpoints_path = data_dir / "endpoints_wordlist.txt"
invalid_mime_type_path = data_dir / "invalid_mime_type.txt"
invalid_extension_path = data_dir / "invalid_extension.pdf"
invalid_size_path = data_dir / "invalid_size.txt"
subdomains_path = data_dir / "subdomains_wordlist.txt"

first_wordlist_name = "Common (dirb)"

wordlist_endpoints = {"name": "test 1", "type": WordlistType.ENDPOINT.value}
new_wordlist_endpoints = {"name": "new test 1", "type": WordlistType.ENDPOINT.value}
wordlist_subdomains = {"name": "test 2", "type": WordlistType.SUBDOMAIN.value}
new_wordlist_subdomains = {"name": "new test 2", "type": WordlistType.SUBDOMAIN.value}


class WordlistTest(ApiTest):
    endpoint = "/api/wordlists/"
    expected_str = first_wordlist_name
    data_dir = data_dir
    cases = [
        ApiTestCase(["reader1", "reader2"], "get", 403),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 1,
                "name": first_wordlist_name,
                "type": WordlistType.ENDPOINT,
                "owner": None,
                "liked": False,
                "likes": 0,
            },
            endpoint="{endpoint}1/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "post",
            400,
            {
                **wordlist_endpoints,
                "file": invalid_mime_type_path.open("rb"),
            },
            format="multipart",
        ),
        ApiTestCase(
            ["admin1"],
            "post",
            201,
            {
                **wordlist_endpoints,
                "file": endpoints_path.open("rb"),
            },
            {
                "id": 29,
                **wordlist_endpoints,
                "size": 3,
                "owner": {"id": 1, "username": "admin1"},
                "liked": False,
                "likes": 0,
            },
            format="multipart",
        ),
        ApiTestCase(
            ["auditor1"],
            "post",
            201,
            {
                **wordlist_subdomains,
                "file": subdomains_path.open("rb"),
            },
            {
                "id": 30,
                **wordlist_subdomains,
                "size": 3,
                "owner": {"id": 3, "username": "auditor1"},
                "liked": False,
                "likes": 0,
            },
            format="multipart",
        ),
        ApiTestCase(
            ["auditor1", "auditor2"],
            "put",
            403,
            new_wordlist_endpoints,
            endpoint="{endpoint}29/",
        ),
        ApiTestCase(
            ["admin1", "admin2"],
            "put",
            200,
            new_wordlist_endpoints,
            {"id": 29, **new_wordlist_endpoints},
            endpoint="{endpoint}29/",
        ),
        ApiTestCase(
            ["auditor2"],
            "put",
            403,
            new_wordlist_subdomains,
            endpoint="{endpoint}30/",
        ),
        ApiTestCase(
            ["auditor1", "admin1", "admin2"],
            "put",
            200,
            new_wordlist_subdomains,
            {"id": 30, **new_wordlist_subdomains},
            endpoint="{endpoint}30/",
        ),
        ApiTestCase(["reader1", "reader2"], "post", 403, endpoint="{endpoint}29/like/"),
        ApiTestCase(["reader1", "reader2"], "delete", 403, endpoint="{endpoint}30/like/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            endpoint="{endpoint}?like=true",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "post",
            204,
            endpoint="{endpoint}29/like/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 29,
                **new_wordlist_endpoints,
                "size": 3,
                "owner": {"id": 1, "username": "admin1"},
                "liked": True,
                "likes": 4,
            },
            endpoint="{endpoint}29/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected=[
                {
                    "id": 29,
                    **new_wordlist_endpoints,
                    "size": 3,
                    "owner": {"id": 1, "username": "admin1"},
                    "liked": True,
                    "likes": 4,
                }
            ],
            endpoint="{endpoint}?like=true",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "delete",
            204,
            endpoint="{endpoint}29/like/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            200,
            expected={
                "id": 29,
                **new_wordlist_endpoints,
                "size": 3,
                "owner": {"id": 1, "username": "admin1"},
                "liked": False,
                "likes": 0,
            },
            endpoint="{endpoint}29/",
        ),
        ApiTestCase(
            ["reader1", "reader2", "auditor1", "auditor2"],
            "delete",
            403,
            endpoint="{endpoint}29/",
        ),
        ApiTestCase(["reader1", "reader2", "auditor2"], "delete", 403, endpoint="{endpoint}30/"),
        ApiTestCase(["admin2"], "delete", 204, endpoint="{endpoint}29/"),
        ApiTestCase(["auditor1"], "delete", 204, endpoint="{endpoint}30/"),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            404,
            endpoint="{endpoint}29/",
        ),
        ApiTestCase(
            ["admin1", "admin2", "auditor1", "auditor2"],
            "get",
            404,
            endpoint="{endpoint}30/",
        ),
    ]

    def setUp(self) -> None:
        super().setUp()
        settings = Settings.objects.first()
        settings.max_uploaded_file_mb = 1
        settings.save(update_fields=["max_uploaded_file_mb"])
        valid_content = endpoints_path.read_text()
        for path in [invalid_extension_path, invalid_size_path]:
            path.write_text(valid_content)
        invalid_size = settings.max_uploaded_file_mb * 1024 * 1024 + 100
        with invalid_size_path.open("a") as file:
            while invalid_size_path.stat().st_size < invalid_size:
                file.write(valid_content)
        self.cases.extend(
            [
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2"],
                    "post",
                    400,
                    {
                        **wordlist_endpoints,
                        "file": invalid_extension_path.open("rb"),
                    },
                    format="multipart",
                ),
                ApiTestCase(
                    ["admin1", "admin2", "auditor1", "auditor2"],
                    "post",
                    400,
                    {
                        **wordlist_endpoints,
                        "file": invalid_size_path.open("rb"),
                    },
                    format="multipart",
                ),
            ]
        )

    def tearDown(self) -> None:
        super().tearDown()
        invalid_extension_path.unlink()
        invalid_size_path.unlink()

    def _get_object(self) -> Any:
        return Wordlist.objects.first()
