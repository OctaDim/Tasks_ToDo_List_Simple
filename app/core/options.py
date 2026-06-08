from dataclasses import dataclass

@dataclass(frozen=True)
class PaginationOptions:
    MAX_LIMIT: int = 1000
    DEFAULT_PAGINATION: int = 100
