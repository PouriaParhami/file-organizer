class FileOrganizerError(Exception):
    """Base exception for file organizer application."""
    pass


class InvalidSourcePath(FileOrganizerError):
    """Raised when the source path is missing or not a directory."""
    pass


class InvalidDestinationPath(FileOrganizerError):
    """Raised when the destination path points to a non-directory target."""
    pass


class PathError(FileOrganizerError):
    """Raised when the source and destination have an invalid relationship."""
    pass


class InsufficientSpaceError(FileOrganizerError):
    """Raised when the destination drive does not have enough free space."""
    pass
