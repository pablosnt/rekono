"""Notes and documentation management module for Rekono.

This module provides note-taking and documentation capabilities for security
teams to capture, organize, and share insights throughout security assessments.
Every note belongs to a project and may optionally be linked to at most one
further entity, such as a target, task, or finding, with collaborative
features like forking, tagging, and like functionality.

Key Features:
    - Contextual note attachment to at most one target, task, or finding entity,
      on top of the project every note always belongs to
    - Collaborative note sharing with public/private visibility controls
    - Note forking system for knowledge base development and sharing
    - Tagging system for note organization and categorization
    - Like/unlike functionality for community-driven content curation
    - Search across note titles and content, plus relationship-based filtering
      that finds notes tied to an entity directly or through related entities
      (for example, a host's ports, paths, and vulnerabilities)
    - User ownership and permission management with access controls

Architecture:
    Every note requires a project, and may optionally also link to one further
    entity such as a target, task, or finding. When a further entity is set,
    the submitted project is overridden with that entity's own project, so
    the note's project always agrees with its linked entity, and only one
    such entity association is kept active at a time. Forking copies a public
    note owned by another user into a new private note that references the
    original; if the original note is later made private, its forks are
    unlinked from it.

Security:
    - Visibility scoped by ownership and project membership: a note is visible
      to its owner always, and to other project members only once marked public
    - Ownership-based permissions restrict edits and deletion to the note's
      owner, with no administrator override
    - Regex-based input validation on note titles to prevent malformed content
"""
