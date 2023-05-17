# Label utils module

The module `kili.utils.labels` provides a set of helpers to convert point, bounding box, polygon and segmentation labels.

!!! info
    In Kili json response format, a normalized vertex is a dictionary with keys `x` and `y` and values between `0` and `1`. The origin is always the top left corner of the image. The x-axis is horizontal and the y-axis is vertical with the y-axis pointing down. You can find more information about the Kili data format [here](https://docs.kili-technology.com/docs/data-format).

## Points

`kili.utils.labels.point`

::: kili.utils.labels.point

## Bounding boxes

`kili.utils.labels.bbox`

::: kili.utils.labels.bbox

## Polygon and segmentation masks

`kili.utils.labels.image`

::: kili.utils.labels.image
