"""Executors that build and run the commands of the tools.

Most tools are run by the base executor, and the ones that need something special,
like moving the report that they write or isolating their working directory, have
their own executor named after them.
"""
