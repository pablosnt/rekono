"""Security tools that Rekono runs, and how they are run and understood.

A tool has one configuration per thing that it can do, and each configuration
declares the arguments that it accepts, the input types that fill them, and the
finding types that it produces, so Rekono can chain the tools without knowing
anything about them. The executors subpackage builds and runs the commands, and
the parsers subpackage turns their output into findings.

All this data comes from the fixtures, so the tools are never created through the
API, only enabled or disabled by whether they are installed in the system.
"""
