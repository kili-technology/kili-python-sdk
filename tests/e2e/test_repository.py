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
def test_get_content_stream_public_image(content_url):
    kili = Kili()
    content_repository = SDKContentRepository(
        kili.auth.api_endpoint,
        router_headers={
            "Authorization": f"X-API-Key: {kili.auth.api_key}",
        },
        verify_ssl=True,
    )

    content_repository.get_content_stream(content_url, 1024)
