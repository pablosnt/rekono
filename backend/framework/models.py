"""Abstract models that the Rekono models are built on.

Provide the features that are shared by several apps: the project that an object
belongs to, the encryption of the secrets, the likes of the users, and the input
system that turns model data into the arguments of the tool executions.
"""

import re
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, cast
from urllib.parse import urljoin, urlparse

import requests
import urllib3
from django.core.exceptions import ValidationError
from django.db.models import ManyToManyField, Model, Q, TextChoices

from framework.cache import Cache
from framework.enums import InputKeyword
from framework.logging import LoggingEntity
from rekono.settings import AUTH_USER_MODEL, CONFIG
from security.cryptography import Crypto
from security.validators.enums import Regex


class BaseModel(Model, LoggingEntity):
    """Base model of all the Rekono models.

    Its subclasses declare the path from themselves to the project that their
    objects belong to, using the Django double underscore notation, so the access
    control can be applied to any model. That path is empty for the models that
    aren't related to a project, which are the ones shared by all of them.
    """

    _project_field = ""

    class Meta:
        """Model configuration, marking it as abstract."""

        abstract = True

    @cached_property
    def parent_project(self) -> Any | list[Any] | None:
        """The project that this object belongs to, following the _project_field path.

        Several projects for the models that are shared by more than one, so the
        callers that check a membership have to accept both shapes. None if this
        model isn't related to a project, or if any reference in that path isn't set
        for this object.
        """
        filter_field = self.__class__._project_field
        if filter_field:
            project = self
            for field in filter_field.split("__"):
                if hasattr(project, field) and getattr(project, field):
                    project = getattr(project, field)
                else:
                    return None
            return project

    def __str__(self) -> str:
        """Return the model name, so all the models have a representation."""
        return self.__class__.__name__


class BaseEncrypted(BaseModel):
    """Base model for the models that store a secret value.

    The secret is encrypted before it's saved and decrypted when it's read through
    the secret property, so the plain value never reaches the database. If no
    encryption key is configured, the value is stored as it is. Its subclasses
    declare which of their fields stores the encrypted value.
    """

    class Meta:
        """Model configuration, marking it as abstract."""

        abstract = True

    _encryptor = Crypto(CONFIG.encryption_key) if CONFIG.encryption_key else None
    _encrypted_field = "_secret"

    @property
    def secret(self) -> str | None:
        """The decrypted secret, or None if this object doesn't have one."""
        return (
            (
                self._encryptor.decrypt(getattr(self, self._encrypted_field))
                if self._encryptor
                else getattr(self, self._encrypted_field)
            )
            if hasattr(self, self._encrypted_field) and getattr(self, self._encrypted_field)
            else None
        )

    @secret.setter
    def secret(self, value: str) -> None:
        """Encrypt a new secret value and assign it to the encrypted field."""
        if hasattr(self, self._encrypted_field):
            setattr(
                self,
                self._encrypted_field,
                (self._encryptor.encrypt(value) if self._encryptor and value is not None else value),
            )


class BaseInput(BaseModel):
    """Base model for the data that can be used as input of the tool executions.

    Its subclasses declare the filters that decide if their data matches the
    conditions of a tool input, the value that they provide for each keyword of the
    argument templates, and the related inputs that must be parsed before them, so
    a finding can complete the keywords of the ones that it was discovered from.
    """

    class Meta:
        """Model configuration, marking it as abstract."""

        abstract = True

    _url_cache = Cache(prefix="url")
    _max_redirects = 5

    @dataclass
    class Filter:
        """One condition that an input must match to be used by a tool argument.

        Attributes:
            type: Type of the values that this filter can evaluate.
            field: Model field whose value is compared against the condition.
            contains: Whether the condition can match a part of the value, instead
              of requiring the whole value to be equal.
            processor: Function applied to the value before comparing it.
        """

        type: type
        field: str
        contains: bool = False
        processor: Callable[[Any], Any] | None = None

        def filter(self, expected: str, value: Any, is_negative: bool = False) -> bool:
            """Check if a value matches the expected one.

            A missing value (None) cannot positively match, but it satisfies a
            negated filter: a value that is absent is "not" anything, so "!cve"
            matches a finding that has no CVE.

            Args:
                expected: Condition that the value should match.
                value: Value of the model field, before being processed.
                is_negative: Whether the condition is negated, so the filter matches
                  the values that are different from the expected one.

            Returns:
                Whether the value matches the condition. False for the values whose
                type this filter can't evaluate.
            """
            if value is None:
                # Negated filter is satisfied because an absent value is "not" anything
                return is_negative
            if self.processor:
                value = self.processor(value)
            try:
                # Choices are compared by name, since the conditions reference the names
                # that the users know, and not the values stored in the database
                return (
                    issubclass(self.type, TextChoices)
                    and self._compare(expected.upper(), cast(TextChoices, self.type)(value).name, is_negative)
                ) or (
                    self.type in [str, int]
                    and self._compare(
                        str(expected).strip().lower(), str(value).strip().lower(), is_negative, self.contains
                    )
                )
            except (ValueError, KeyError):  # pragma: no cover
                return False

        def _compare(self, expected: str, value: str, negative: bool = False, contains: bool = False) -> bool:
            """Compare two values, optionally by substring and with a negated result.

            Args:
                expected: Condition that the value should match, already processed.
                value: Value of the model field, already processed.
                negative: Whether the result of the comparison must be inverted.
                contains: Whether the expected value only has to be a part of the
                  value, instead of the whole value.

            Returns:
                Whether the two values match, after applying the negation.
            """
            conclusion = expected == value if not contains else expected in value
            return conclusion if not negative else not conclusion

        def is_applicable(self, condition: str) -> bool:
            """Whether this filter's type can evaluate the given condition token.

            An int filter evaluates only numeric tokens, a str filter only
            non-numeric tokens, and a TextChoices filter only its own enum names.
            BaseInput.filter uses this to skip filters that can't judge a condition,
            so a condition outside the types a model tracks never drops it.

            Args:
                condition: A single filter condition, already stripped of "!".

            Returns:
                Whether this filter is able to judge that condition.
            """
            if issubclass(self.type, TextChoices):
                return condition.strip().upper() in self.type.names
            is_digit = condition.strip().isdigit()
            return is_digit if self.type is int else not is_digit

    _filters: list[Filter] = []
    _parse_mapping: dict[InputKeyword, str | Callable | dict[str, str]] = {}
    _parse_dependencies: list[str] = []

    @cached_property
    def input_type(self) -> Any:
        """The input type that references this model, or None if there isn't any.

        The input types reference their models by app and model name, either as
        their main model or as the fallback used when no finding is available yet.
        """
        from input_types.models import InputType

        reference = f"{self._meta.app_label}.{self._meta.model_name}"
        return InputType.objects.filter(Q(model=reference) | Q(fallback_model=reference)).first()

    @staticmethod
    def clean_path(value: str | None) -> str | None:
        """Normalize a path string by ensuring it starts with a forward slash.

        Defined as a static method so parsers can normalize a raw path value before
        creating a Path finding, keeping deduplication consistent regardless of whether
        the source tool reports the leading slash (e.g. gobuster emits ``images`` while
        dirsearch emits ``/images``).

        A leading ``:<port>`` left over from a parsed URL is stripped as well (e.g.
        ``/:80/images`` and ``:80/images`` both become ``/images``), which happens when a
        tool reports paths built by splitting a full URL by its host. This is generic so
        no caller needs to know the port.

        Args:
            value: Raw path as the tool reported it, or None.

        Returns:
            The normalized path with leading slash, "/" for an empty string, or None
            when the value is None (so callers omit the argument).
        """
        if value is None:
            return None
        # Drop a leading ":<port>" with or without a leading slash
        value = re.sub(r"^/?:\d+(?=/|$)", "", value)
        if len(value) > 1 and value[0] != "/":
            value = f"/{value}"
        return "/" if not value else value

    def _is_allowed_url(self, url: str, source_url: str) -> bool:
        """Check that a URL can be requested, before any connection is made to it.

        Only HTTP and HTTPS URLs whose host would be accepted as a target by the target
        validation policy are allowed, so a redirect can't move a scan onto a host that
        could never have been set as a target, like the platform's own internal services.

        Args:
            url: The URL that is about to be requested.
            source_url: The URL that redirected to it, used to report the rejection.

        Returns:
            Whether the URL can be requested. A rejection is logged as a security
            warning before returning False.
        """
        from security.validators.target_validator import TargetValidator

        parsed_url = urlparse(url)
        if parsed_url.scheme not in ["http", "https"]:
            self.logger.warning(f"[Security] HTTP GET {source_url} redirects to {url}, whose schema isn't supported")
            return False
        try:
            TargetValidator(Regex.TARGET)(parsed_url.hostname)
        except ValidationError as error:
            self.logger.warning(
                f"[Security] HTTP GET {source_url} redirects to {url} which is a target denied by policy: {' '.join(error.messages)}"
            )
            return False
        return True

    def _get_url_with_redirects(self, url: str) -> str | None:
        """Probe a URL and follow its redirects, checking each one before requesting it.

        The HTTP client doesn't follow redirects, so each hop is resolved and validated
        against the target validation policy first, and the request is only issued once
        that hop is allowed. This way a denied resource is never contacted, not even as
        an intermediate step of the redirection chain that ends up somewhere allowed.

        Args:
            url: First URL of the chain, which is requested without being validated,
              since it was built from data that is already within the scope.

        Returns:
            The final URL of the redirection chain, or None when one of its hops is
            denied by policy.

        Raises:
            RuntimeError: If the redirection chain loops or doesn't end within
              _max_redirects hops, so callers treat it like any other failed probe.
        """
        requested_urls: list[str] = []
        while url not in requested_urls and len(requested_urls) < self._max_redirects:
            requested_urls.append(url)
            # Use disabled SSL verification for testing purposes and short timeout for efficiency
            # nosemgrep: python.requests.security.disabled-cert-validation.disabled-cert-validation
            response = requests.get(url, timeout=20, verify=False, allow_redirects=False)
            location = response.headers.get("Location") if response.is_redirect else None
            if not location:
                return url
            # A relative location is resolved against the URL that returned it
            url = urljoin(url, location)
            if not self._is_allowed_url(url, requested_urls[-1]):
                return None
        raise RuntimeError(f"URL {requested_urls[0]} has too many redirects")

    def get_url(
        self,
        host: str,
        port: int | None = None,
        endpoint: str | None = None,
        protocols: list[str] = ["https", "http"],
        task: Any = None,
    ) -> str | None:
        """Build the URL of a web service, probing it to know which one works.

        Each protocol and port combination is looked up in _url_cache before issuing
        a request, and the resulting URL is cached afterwards, so repeated calls for
        the same URL (e.g. across multiple tool arguments) don't repeat the same HTTP
        request and get the same redirections. Redirections are checked against the
        target validation policy before being requested, so a redirect can't move a
        scan onto a host that could never have been set as a target, and no request
        is ever sent to a denied one.

        Args:
            host: Hostname or IP address of the web service.
            port: Port of the web service. When set, only this port is probed and
              the task scope is ignored.
            endpoint: Path to be appended to the URL, with or without leading slash.
            protocols: Protocols to probe, in the order they should be tried.
            task: Task whose scoped target ports are probed when no explicit port is
              given. Without a task, the common web ports are probed instead.

        Returns:
            The URL that answered the request, after following its redirects, or
            None if none of the combinations works. Also None when the URL redirects
            to a denied target, without falling back to another port or protocol,
            because the host already tried to move the scan out of its allowed scope.
        """
        # Disable SSL warnings since we're testing connectivity with disabled certificate verification
        urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

        # The slash between the port and the endpoint is already in the schema
        if endpoint is None:
            endpoint = ""
        elif endpoint.startswith("/"):
            endpoint = endpoint[1:]
        schema = "{protocol}://{host}:{port}/{endpoint}"
        default_ports = [443, 80]
        if port:
            ports = [port]
        elif task is not None:
            ports = set([tp.port for tp in task.get_scoped_target_ports()]) or default_ports
        else:
            ports = default_ports
        for port in ports:
            for protocol in protocols:
                # Don't try HTTPS on port 80 or HTTP on port 443 when both protocols are
                # available, since the other combination will be tried anyway
                if len(protocols) > 1 and (
                    (port == 80 and protocol == "https") or (port == 443 and protocol == "http")
                ):
                    continue
                url_to_test = schema.format(protocol=protocol, host=host, port=port, endpoint=endpoint)
                cached_result = self._url_cache.get(url_to_test)
                if cached_result is not None:
                    # "0" is the cached mark of a URL that didn't answer a previous probe
                    if cached_result == "0":
                        continue
                    return cached_result
                try:
                    working_url = self._get_url_with_redirects(url_to_test)
                except Exception:
                    self._url_cache.set(url_to_test, "0")
                    continue
                if not working_url:
                    return None
                self._url_cache.set(url_to_test, working_url)
                return working_url

    def filter(self, argument_input: Any, target: Any = None) -> bool:
        """Check if this object matches the conditions required by a tool input.

        The conditions are combined with "and" or "or", and a condition prefixed
        with "!" is negated. Each condition is evaluated only by the filters that
        apply to it (see Filter.is_applicable). A condition that no filter can
        evaluate does not constrain the input, so a model is never dropped by a
        condition outside the types it tracks (for example a service name against a
        target port that only knows its port number).

        Args:
            argument_input: Tool input whose filter conditions must be matched.
            target: Target of the execution, only used by the subclasses that need
              to check the input against the target scope.

        Returns:
            Whether this object can be used by that tool input. True when the input
            has no conditions.
        """
        if not argument_input.filter:
            return True
        operator, is_or = (" or ", True) if " or " in argument_input.filter else (" and ", False)
        conclusions = []
        for raw_condition in argument_input.filter.split(operator):
            is_negative = raw_condition.startswith("!")
            condition = raw_condition[1:] if is_negative else raw_condition
            applicable = [f for f in self._filters if f.is_applicable(condition)]
            if not applicable:
                conclusions.append(True)
            else:
                conclusions.append(any(f.filter(condition, getattr(self, f.field), is_negative) for f in applicable))
        return any(conclusions) if is_or else all(conclusions)

    def parse(self, task: Any, accumulated: dict[str, Any] = {}) -> dict[str, Any]:
        """Get the keywords provided by this object to build the tool arguments.

        The dependencies are parsed first, so an object completes the keywords of
        the objects it belongs to, like a port that adds the host it was found in.

        Args:
            task: Task of the execution, forwarded to the parse mappings that build
              URLs so probing stays within the task's target port scope. May be None
              when no task is available.
            accumulated: Keywords already provided by the other inputs of the same
              execution, so lists and dictionaries are extended instead of replaced.

        Returns:
            The keywords provided by this object, ready to format the arguments.
        """
        result = {}
        for dependency in self._parse_dependencies:
            if (
                hasattr(self, dependency)
                and getattr(self, dependency)
                and isinstance(getattr(self, dependency), BaseInput)
            ):
                result.update(getattr(self, dependency).parse(task))
        for keyword, field_or_function in self._parse_mapping.items():
            value = (
                getattr(self, field_or_function)
                if isinstance(field_or_function, str) and hasattr(self, field_or_function)
                else (field_or_function(self, task) if callable(field_or_function) else field_or_function)
            )
            if value is None:
                continue
            key = keyword.name.lower()
            current_value = accumulated.get(key)
            if current_value is not None:
                if isinstance(current_value, list):
                    result[key] = accumulated.get(key, []) + (value if isinstance(value, list) else [value])
                    continue
                elif isinstance(current_value, dict) and isinstance(value, dict):
                    result[key] = {**accumulated.get(key, {}), **value}
                    continue
            result[key] = value
        return result

    def create_finding_from_user_input(self, execution: Any, **fields: Any) -> Any | None:
        """Create the finding equivalent to this input, if the model has one.

        Overridden by the inputs provided by the auditors, so the findings that the
        tools report can be related to the data that the auditor supplied.

        Args:
            execution: Execution that the created finding belongs to.
            **fields: Extra values for the finding, currently only the port where a
              technology or a vulnerability supplied by the auditor was found.

        Returns:
            None, unless the model overrides this method.
        """
        return None  # pragma: no cover


class BaseLike(BaseModel):
    """Base model for the models that the users can like.

    Attributes:
        liked_by: Users that liked each object.
    """

    liked_by = ManyToManyField(AUTH_USER_MODEL, related_name="liked_%(class)s")

    class Meta:
        """Model configuration, marking it as abstract."""

        abstract = True
