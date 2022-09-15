from typing import Any, Dict, Iterator, List

from kili.services.export.repository import AbstractContentRepository


class FakeContentRepository(AbstractContentRepository):
    def get_frames(self, content_url: str, router_headers: Dict) -> List[str]:
        return []

    def get_content_stream(
        self, content_url: str, block_size: int, router_headers: Dict
    ) -> Iterator[Any]:
        for i in []:
            yield i
