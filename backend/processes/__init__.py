"""Processes, which are reusable groups of tool configurations to be executed.

A process is a set of steps, and each step references the tool configuration that
it runs. The steps carry no order of their own: when a process is executed, the
task engine resolves the run order from the stage of each tool, and chains the
steps whose output type matches the input type of another one.
"""
