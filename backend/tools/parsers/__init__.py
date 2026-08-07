"""Parsers that turn the output of the tools into findings.

Each parser is named after its tool and only implements how to read its output,
which can be JSON, XML, or plain text. The tools whose output reports nothing that
Rekono understands use the base parser, so they discover no findings.
"""
