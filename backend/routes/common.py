from fastapi import Query
from typing import Annotated

class ListCommons:
    def __init__(self,
        limit: Annotated[int, Query(le=100)] = 100,
        skip: int = 0,
    ):
        self.limit = limit
        self.skip = skip
