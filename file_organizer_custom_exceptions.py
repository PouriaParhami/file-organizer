class FileOrganizerError(Exception):
    """Base exception for file organizer application."""
    pass


class InvalidSourcePath(FileOrganizerError):
    pass


class InvalidDestinationPath(FileOrganizerError):
    pass


class PathError(FileOrganizerError):
    pass


class InsufficientSpaceError(FileOrganizerError):
    pass