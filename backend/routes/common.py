from typing import Annotated

from fastapi import Query


class ListCommons:
    def __init__(self,
        limit: Annotated[int, Query(le=100)] = 100,
        skip: int = 0,
    ):
        self.limit = limit
        self.skip = skip
