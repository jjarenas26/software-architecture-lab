from typing import Protocol

from app.models import ProcessingContext


class Filter(Protocol):
    name: str

    def process(self, context: ProcessingContext) -> ProcessingContext: ...


class Pipeline:
    def __init__(self, filters: list[Filter]) -> None:
        self.filters = filters

    def execute(self, context: ProcessingContext) -> ProcessingContext:
        for filter_ in self.filters:
            context = filter_.process(context)
        return context
