"""Findings, which are everything that the tools discover about the targets.

There is one model per kind of finding, from the OSINT data to the vulnerabilities
and their exploits, and they reference each other to keep the context of the
discovery, so a vulnerability knows the port and the host where it was found. The
findings are also inputs of the executions, so what one tool discovers becomes the
input of the next one.
"""
