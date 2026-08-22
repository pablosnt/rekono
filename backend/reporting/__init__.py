"""Reports that export the findings of a project, a target, or a task.

The reports are generated in the background, since a big scope can take a while,
and the result is stored as a file that the users download later. The JSON and XML
reports export the findings as they are, while the PDF one is a document meant to
be read, so it decides its content itself.
"""
