import pytest

from kili.client import Kili
from kili.services.export import SDKContentRepository


@pytest.mark.parametrize(
    "content_url",
    [
        "https://storage.googleapis.com/label-public-staging/car/car_2.jpg",
        "https://storage.googleapis.com/label-public-staging/car/car_1.jpg",
    ],
)
def test_get_content_stream_public_image(kili: Kili, content_url):
    content_repository = SDKContentRepository(kili.api_endpoint, http_client=kili.http_client)

    content_repository.get_content_stream(content_url, 1024)
