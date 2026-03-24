class BothPathWrong(Exception):
    """Custom exception for when both addresses are invalid."""
    pass

class DestinationPathWrong(Exception):
    """Custom exception for when Destination addresses are invalid."""
    pass

class SourcePathWrong(Exception):
    """Custom exception for when seouce addresses are invalid."""
    pass

class NotEnoughSpace(Exception):
    """Custom exception for when Destination path do not have enough space."""
    pass

