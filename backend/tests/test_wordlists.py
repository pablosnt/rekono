from functools import cached_property

from django.core.management import call_command
from django.test import TestCase

from security.authorization.roles import Role
from settings.models import Settings
from tests.framework import ApiTestNoData
from tests.framework.cases import ApiTestCase, DeleteApiTestCase, PostApiTestCase, PutApiTestCase
from tools.models import Input
from wordlists.enums import WordlistType
from wordlists.models import Wordlist

# pytype: disable=wrong-arg-types

# Wordlists paths
data_dir = ApiTestNoData.data_dir / "wordlists"
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


class WordlistTest(ApiTestNoData, TestCase):
    endpoint = "/api/wordlists/"
    expected_string = first_wordlist_name

    @cached_property
    def cases(self) -> list[ApiTestCase]:
        return [
            ApiTestCase([Role.READER], 403),
            ApiTestCase(
                [Role.ADMIN, Role.AUDITOR],
                expected={
                    "id": 1,
                    "name": first_wordlist_name,
                    "type": WordlistType.ENDPOINT,
                    "owner": None,
                    "liked": False,
                    "likes": 0,
                },
                endpoint="1",
            ),
            PostApiTestCase(
                [Role.ADMIN, Role.AUDITOR],
                400,
                {**wordlist_endpoints, "file": invalid_mime_type_path.open("rb")},
                format="multipart",
            ),
            PostApiTestCase(
                ["admin1"],
                data={**wordlist_endpoints, "file": endpoints_path.open("rb")},
                expected={"id": 58, **wordlist_endpoints, "size": 3, "owner": {"id": 1, "username": "admin1"}},
                format="multipart",
            ),
            PostApiTestCase(
                ["auditor1"],
                data={**wordlist_subdomains, "file": subdomains_path.open("rb")},
                expected={"id": 59, **wordlist_subdomains, "size": 3, "owner": {"id": 3, "username": "auditor1"}},
                format="multipart",
            ),
            PutApiTestCase([Role.AUDITOR], 403, new_wordlist_endpoints, endpoint="58"),
            PutApiTestCase(
                [Role.ADMIN], data=new_wordlist_endpoints, expected={"id": 58, **new_wordlist_endpoints}, endpoint="58"
            ),
            PutApiTestCase(["auditor2"], 403, new_wordlist_subdomains, endpoint="59"),
            PutApiTestCase(
                ["auditor1", Role.ADMIN],
                data=new_wordlist_subdomains,
                expected={"id": 59, **new_wordlist_subdomains},
                endpoint="59",
            ),
            PostApiTestCase([Role.READER], 403, endpoint="58/like"),
            DeleteApiTestCase([Role.READER], 403, endpoint="59/like"),
            ApiTestCase([Role.ADMIN, Role.AUDITOR], endpoint="{endpoint}?like=true"),
            PostApiTestCase([Role.ADMIN, Role.AUDITOR], 204, endpoint="58/like"),
            ApiTestCase(
                [Role.ADMIN, Role.AUDITOR],
                expected={
                    "id": 58,
                    **new_wordlist_endpoints,
                    "size": 3,
                    "owner": {"id": 1, "username": "admin1"},
                    "liked": True,
                    "likes": 4,
                },
                endpoint="58",
            ),
            ApiTestCase(
                [Role.ADMIN, Role.AUDITOR],
                expected=[
                    {
                        "id": 58,
                        **new_wordlist_endpoints,
                        "size": 3,
                        "owner": {"id": 1, "username": "admin1"},
                        "liked": True,
                        "likes": 4,
                    }
                ],
                endpoint="{endpoint}?like=true",
            ),
            DeleteApiTestCase([Role.ADMIN, Role.AUDITOR], endpoint="58/like"),
            ApiTestCase(
                [Role.ADMIN, Role.AUDITOR],
                expected={
                    "id": 58,
                    **new_wordlist_endpoints,
                    "size": 3,
                    "owner": {"id": 1, "username": "admin1"},
                    "liked": False,
                    "likes": 0,
                },
                endpoint="58",
            ),
            DeleteApiTestCase([Role.READER, Role.AUDITOR], 403, endpoint="58"),
            DeleteApiTestCase([Role.READER, "auditor2"], 403, endpoint="59"),
            DeleteApiTestCase(["admin2"], endpoint="58"),
            DeleteApiTestCase(["auditor1"], endpoint="59"),
            ApiTestCase([Role.ADMIN, Role.AUDITOR], 404, endpoint="58"),
            ApiTestCase([Role.ADMIN, Role.AUDITOR], 404, endpoint="59"),
            PostApiTestCase(
                [Role.ADMIN, Role.AUDITOR],
                400,
                {**wordlist_endpoints, "file": invalid_extension_path.open("rb")},
                format="multipart",
            ),
            PostApiTestCase(
                [Role.ADMIN, Role.AUDITOR],
                400,
                {**wordlist_endpoints, "file": invalid_size_path.open("rb")},
                format="multipart",
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

    def tearDown(self) -> None:
        super().tearDown()
        invalid_extension_path.unlink()
        invalid_size_path.unlink()

    def test_update_wordlists_size_command(self) -> None:
        wordlist = Wordlist.objects.create(name="test size", type=WordlistType.ENDPOINT, path=str(endpoints_path))
        missing = Wordlist.objects.create(name="test missing", type=WordlistType.ENDPOINT, path="/does/not/exist")
        call_command("update_wordlists_size")
        wordlist.refresh_from_db()
        missing.refresh_from_db()
        self.assertEqual(len(endpoints_path.read_text().splitlines()), wordlist.size)
        self.assertIsNone(missing.size)

    def test_base_input_filter(self) -> None:
        wordlist = Wordlist(type=WordlistType.ENDPOINT, path=str(endpoints_path))
        self.assertTrue(wordlist.filter(Input(filter="endpoint")))
        self.assertFalse(wordlist.filter(Input(filter="subdomain")))
        # OR
        self.assertTrue(wordlist.filter(Input(filter="endpoint or subdomain")))
        # Negation
        self.assertTrue(wordlist.filter(Input(filter="!subdomain")))
        self.assertFalse(wordlist.filter(Input(filter="!endpoint")))
        # Empty filter
        self.assertTrue(wordlist.filter(Input(filter="")))
        # Not existing path
        self.assertFalse(Wordlist(type=WordlistType.ENDPOINT, path="/does/not/exist").filter(Input(filter="endpoint")))

    @cached_property
    def object(self) -> Wordlist:
        return Wordlist.objects.first()
