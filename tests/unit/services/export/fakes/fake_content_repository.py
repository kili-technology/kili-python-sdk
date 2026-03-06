from collections.abc import Iterator
from typing import Any

from kili.services.export.repository import AbstractContentRepository


class FakeContentRepository(AbstractContentRepository):
    def get_frames(self, content_url: str) -> list[str]:
        return []

    def get_content_stream(self, content_url: str, block_size: int) -> Iterator[Any]:
        yield from []
