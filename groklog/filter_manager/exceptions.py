class FilterError(Exception):
    pass


class DuplicateFilterError(FilterError):
    pass


class FilterNotFoundError(FilterError):
    pass
