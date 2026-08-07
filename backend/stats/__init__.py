"""Statistics calculated from the findings and from the background jobs.

The endpoints are read only and they aggregate the data in the database, so the
frontend can draw the charts without having to request all the findings and count
them itself. Everything is scoped to the projects that the user belongs to, except
the queue statistics, which are about the whole deployment.
"""
