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

!!! info "OpenCV"
    It is recommended to install the image dependencies to use the image helpers.
    ```bash
    pip install kili[image-utils]
    ```

::: kili.utils.labels.image

## GeoJson

!!! info Geospatial imagery
    Label coordinates of GeoTIFF files (with geospatial metadata) are expressed in latitude and longitude where `x` stands for longitude and `y` for latitude.

    Read more about Kili labeling features for geospatial imagery [here](https://docs.kili-technology.com/docs/geospatialtiled-imagery).

### Point

::: kili.utils.labels.geojson.point

### Line

::: kili.utils.labels.geojson.line

### Bounding box

::: kili.utils.labels.geojson.bbox

### Polygon

::: kili.utils.labels.geojson.polygon

### Segmentation

::: kili.utils.labels.geojson.segmentation

### Collection

::: kili.utils.labels.geojson.collection
