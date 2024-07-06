from findings.enums import Severity
from findings.models import Technology, Vulnerability
from tools.parsers.base import BaseParser


class Sshaudit(BaseParser):
    cryptography_types = {
        "kex": "key exchange",
        "key": "host key",
        "enc": "encryption",
        "mac": "MAC",
    }

    def _parse_standard_output(self) -> None:
        algorithms: dict[str, list[str]] = {
            k: [] for k in self.cryptography_types.keys()
        }
        technology = None
        vulnerabilities_to_create = []
        for line in self.output.split("\n"):  # Get output by lines
            data = line.strip()
            if "(gen) software: " in data:
                aux = data.split("(gen) software: ", 1)[1].split(" ", 1)
                technology = self.create_finding(
                    Technology, name=aux[0], version=aux[1].split(" [", 1)[0]
                )
            elif "(cve) " in data:
                aux = data.split("(cve) ", 1)[1].split(" ", 1)
                vulnerabilities_to_create.append(
                    (aux[1].split(") ", 1)[1].split(" [", 1)[0].capitalize(), aux[0])
                )
            else:
                for cryptography_type in algorithms.keys():
                    if f"({cryptography_type}) " in data and "[fail]" in data:
                        algorithm = data.split(f"({cryptography_type}) ", 1)[1].split(
                            " ", 1
                        )[0]
                        if algorithm not in algorithms[cryptography_type]:
                            algorithms[cryptography_type].append(algorithm)
                        break
        for name, cve in vulnerabilities_to_create:
            self.create_finding(
                Vulnerability, technology=technology, name=name, cve=cve
            )
        for key, vulnerable_algorithms in algorithms.items():
            if len(vulnerable_algorithms) > 0:
                self.create_finding(
                    Vulnerability,
                    technology=technology,
                    name=f"Insecure {self.cryptography_types[key]} algorithms",
                    description=", ".join(vulnerable_algorithms),
                    severity=Severity.LOW,
                    # CWE-326: Inadequate Encryption Strength
                    cwe="CWE-326",
                )
