class DataLoadError(Exception):
    """Raised when sales data cannot be loaded from the API."""
    pass


class SaveToDiskError(Exception):
    """Raised when data cannot be saved to disk."""
    pass

class NoSalesDataFound(Exception):
    """Raised when API returns empty data for the given date."""
    pass
