<!-- FILE AUTO GENERATED BY docs/utils.py DO NOT EDIT DIRECTLY -->
<a href="https://colab.research.google.com/github/kili-technology/kili-python-sdk/blob/main/recipes/importing_multilayer_geosat_assets.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# How to import multi-layer geosat assets to a Kili project

In this tutorial, we will learn how to import multi-layer geosat assets to your project.

Here are the steps that we will follow:

1. Setting up an image project.
2. Importing some multi-layer assets to Kili with GEOTIFFs and layers from a public tile server.

## Setting up a Kili image project to work with

### Installing and instantiating Kili

First, let's install and import the required modules.


```python
%pip install kili
```


```python
from kili.client import Kili
```

Now, let's set up variables needed to create an instance of the Kili object.

We will need your API key and Kili's API endpoint.

If you are unsure how to look up your API key, refer to [https://docs.kili-technology.com/docs/creating-an-api-key](https://docs.kili-technology.com/docs/creating-an-api-key).


```python
api_key = "YOUR_API_KEY"
api_endpoint = "https://cloud.kili-technology.com/api/label/v2/graphql"
kili = Kili(
    # api_endpoint=api_endpoint, api_key=api_key, verify=True
    # the line above can be uncommented and changed if you are working with an on-premise version of Kili
)
```

### Creating an image Kili project

To create an IMAGE Kili project, you must first set up its ontology.

Here, we will only add a classification task:


```python
interface = {
    "jobs": {
        "OBJECT_DETECTION_JOB": {
            "content": {
                "categories": {
                    "PLANE": {
                        "children": [],
                        "color": "#472CED",
                        "name": "Plane",
                        "id": "category3",
                    }
                },
                "input": "radio",
            },
            "instruction": "BBOX",
            "mlTask": "OBJECT_DETECTION",
            "required": 0,
            "tools": ["rectangle"],
            "isChild": False,
            "isNew": False,
        }
    }
}

project = kili.create_project(
    title="[Kili SDK Notebook]: Importing multi-layer Geosatellite asset",
    description="Project Description",
    input_type="IMAGE",
    json_interface=interface,
)
```

## Importing your assets

### Download geotiff file examples

Before adding assets you need to download our geotiff examples and add them in a geosat folder, created in the same folder as where you run your python script. It is mandatory to use local files and not urls for geosatellite files.


```python
import os
import urllib.request

if not os.path.exists("geosat"):
    os.makedirs("geosat")
urllib.request.urlretrieve(
    "https://storage.googleapis.com/label-public-staging/asset-test-sample/geosat/a.tiff",
    "geosat/a.tiff",
)
urllib.request.urlretrieve(
    "https://storage.googleapis.com/label-public-staging/asset-test-sample/geosat/b.tiff",
    "geosat/b.tiff",
)
```

### Add Multi-Layer assets to your project

You can now add assets. Here is an example to add 2 geotiffs and a public layer coming from the openstreetmap tile server.


```python
project_id = project["id"]
json_metadata_array = [{"processingParameters": {"epsg": 3857}}]
multi_layer_content_array = [
    [
        {
            "path": "geosat/a.tiff",
            "name": "Layer 1",
            "isBaseLayer": False,
        },
        {
            "path": "geosat/b.tiff",
            "name": "Layer 2",
            "isBaseLayer": False,
        },
    ],
]
json_content_array = [
    [
        {
            "name": "osm",
            "tileLayerUrl": "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "epsg": "EPSG3857",
            "bounds": [
                [11.17010498046875, 44.308941579503745],
                [13.67478942871094, 46.542667432984864],
            ],
            "useClassicCoordinates": False,
            "minZoom": 10,
            "maxZoom": 18,
            "isBaseLayer": True,
        }
    ]
]

kili.append_many_to_dataset(
    project_id=project_id,
    multi_layer_content_array=multi_layer_content_array,
    json_metadata_array=json_metadata_array,
    json_content_array=json_content_array,
)
```

In this example 4 arguments are used for the `append_many_to_dataset` function :

1. `project_id`: the id of the project to which you want to add the asset
1. `multi_layer_content_array`: it is a list of dictionnaries representing the layers created from geosatellite files like GEOTIFFS. For each GEOTIFF you have to set the `path` to the GEOTIFF, the `name` that will be used in kili for the layer and the boolean `isBaseLayer` to define if it's a base layer (only one visible at a time) or an overlay layer (a layer that will be displayed on top of the base layer). This last one is optional and by default if no parameter is set, we consider it is a base layer.
1. `json_metadata_array`: This one contains the processing parameters that will be used when processing the files. 3 parameters can be set there :
    1. `epsg`: This one defines the projection (<https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset>) to which we will reproject the dataset. Our frontend supports only two projections : `EPSG:4326` and `EPSG:3857`. If this parameter is not set we will keep the projection of the initial file if it is one of these two, else we will reproject it by default to `EPSG:3857`. By default, we advise to not set this parameter but if you need to use your GEOTIFFS with some tile server (as with openstreetmap here) you will need to reproject it to the same EPSG as the one used by the tile server as our application supports only one EPSG for the whole asset. For your information most of the well known tile server (openstreetmap, googlemaps, etc) are using `EPSG:3857`.
    1. `maxZoom` and `minZoom`: these defines limits of zoom for your GEOTIFF files. This is especially useful for files that will be tiled by our server (file size > 30MB). By default we generate all the zooms until the one of the original file but if you want to limit to specific zoom levels you can constrain them with these parameters.
1. `json_content_array`: It has to be used when you need to add public tile layers to your asset. You can find the same arguments as for GEOTIFF layers `name`, `minZoom`, `maxZoom`, `isBaseLayer`. You also need to specify the `epsg` but with the format `EPSG{number}` (this one correspond to the EPSG used by the tile server, we will not reproject anything). And then, you have to provide the url to the tile server with the parameter `tileLayerUrl` and the `bounds`, corresponding to the minimum and maximum latitude and longitude for which you want to request tiles (use the following format `[[min_lng, min_lat],[max_lng, max_lat]]`). Finally, the `useClassicCoordinates: False` has always to be provided to explain that geospatial coordinates are used.

## Cleanup

We can remove the project that we created if needed:


```python
kili.delete_project(project_id)
```
