"""Shapefile to Kili annotations converter.

This module provides functions for reading and processing Shapefile (.shp) files,
extracting their geometries (points, polylines, polygons), and converting them into
a JSON response for geospatial annotations.
"""


import struct
from typing import Dict, List, Optional, Tuple, Union, cast

import pyproj
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.ops import transform


def read_shapefile_header(file_handle):
    """Reads the shapefile header (100 bytes) which contains metadata about the file.

    Shapefile header structure:
    - Bytes 0-3: File code (should be 9994)
    - Bytes 4-23: Unused
    - Bytes 24-27: File length in 16-bit words
    - Bytes 28-31: Version (should be 1000)
    - Bytes 32-35: Shape type
    - Bytes 36-67: Bounding box (min/max X, Y)
    - Bytes 68-83: Z range (min/max)
    - Bytes 84-99: M range (min/max)

    For this function, we just skip the header as we're only interested in the record data.
    """
    file_handle.seek(100)


def read_point_record(file_handle) -> Point:
    """Reads a Point (type 1) record from the shapefile."""
    # Read X and Y coordinates (double precision floating point numbers)
    x, y = struct.unpack("<dd", file_handle.read(16))
    return Point(x, y)


def read_polyline_record(file_handle) -> List[LineString]:
    """Reads a Polyline (type 3) record from the shapefile."""
    # Skip the bounding box (4 doubles = 32 bytes)
    file_handle.read(32)

    # Read number of parts and points
    num_parts, num_points = struct.unpack("<ii", file_handle.read(8))

    # Read the starting index of each part
    parts = struct.unpack("<" + "i" * num_parts, file_handle.read(4 * num_parts))

    # Read all points (x,y pairs)
    all_points = []
    for i in range(num_points):
        x, y = struct.unpack("<dd", file_handle.read(16))
        all_points.append((x, y))

    # Extract each part as a LineString
    polylines = []
    for i in range(num_parts):
        start = parts[i]
        end = num_points if i == num_parts - 1 else parts[i + 1]

        part_points = all_points[start:end]
        if len(part_points) >= 2:  # Valid polyline part (at least 2 points)
            polylines.append(LineString(part_points))

    return polylines


def read_polygon_record(file_handle) -> List[Polygon]:
    """Reads a Polygon (type 5) record from the shapefile."""
    # Skip the bounding box (4 doubles = 32 bytes)
    file_handle.read(32)

    # Read number of parts and points
    num_parts, num_points = struct.unpack("<ii", file_handle.read(8))

    # Read the starting index of each part
    parts = struct.unpack("<" + "i" * num_parts, file_handle.read(4 * num_parts))

    # Read all points (x,y pairs)
    all_points = []
    for i in range(num_points):
        x, y = struct.unpack("<dd", file_handle.read(16))
        all_points.append((x, y))

    # Extract each ring
    rings = []
    for i in range(num_parts):
        start = parts[i]
        end = num_points if i == num_parts - 1 else parts[i + 1]

        ring_points = all_points[start:end]

        if len(ring_points) >= 3:  # Valid ring
            ring = LinearRing(ring_points)
            # In shapefiles, exterior rings are clockwise
            is_exterior = not ring.is_ccw
            rings.append((ring, ring_points, is_exterior))

    exterior_rings = [(ring, points) for ring, points, is_ext in rings if is_ext]
    interior_rings = [(ring, points) for ring, points, is_ext in rings if not is_ext]

    # Create polygons with holes
    polygons = []
    for _, ext_points in exterior_rings:
        ext_poly = Polygon(ext_points)

        # Find interior rings contained by this exterior
        holes = []
        for int_ring, int_points in interior_rings:
            # Check if the interior ring is inside the exterior polygon
            int_centroid = int_ring.centroid
            if ext_poly.contains(int_centroid):
                holes.append(int_points)

        # Create polygon with holes
        if holes:
            polygon = Polygon(ext_points, holes)
        else:
            polygon = ext_poly

        polygons.append(polygon)

    return polygons


def read_shape_record(
    file_handle,
) -> Optional[Tuple[int, Union[Point, List[LineString], List[Polygon]]]]:
    """Reads a single shape record from the shapefile.

    Returns a tuple (shape_type, geometry) where geometry depends on shape_type.
    """
    # Try to read record header
    record_header = file_handle.read(8)
    if len(record_header) < 8:
        return None  # End of file reached

    # Extract content length for potential skipping later
    content_length = struct.unpack(">i", record_header[4:])[0] * 2

    # Read shape type
    shape_type_data = file_handle.read(4)
    if len(shape_type_data) < 4:
        return None  # Unexpected end of file

    shape_type = struct.unpack("<i", shape_type_data)[0]

    if shape_type == 1:  # Point
        return shape_type, read_point_record(file_handle)
    if shape_type == 3:  # Polyline
        return shape_type, read_polyline_record(file_handle)
    if shape_type == 5:  # Polygon
        return shape_type, read_polygon_record(file_handle)
    # Unsupported geometry type - skip to next record
    # Subtract 4 because we already read the shape type
    file_handle.seek(content_length - 4, 1)
    return None


def read_shapefile(filename):
    """Reads a shapefile and extracts geometries."""
    points = []
    polyline_records = []
    polygon_records = []

    with open(filename, "rb") as f:
        read_shapefile_header(f)

        record_id = 0

        while True:
            record = read_shape_record(f)
            if record is None:
                break  # End of file

            shape_type, geometry = record

            if shape_type == 1 and geometry:  # Point
                points.append({"record_id": record_id, "geometry": geometry})
                record_id += 1
            elif shape_type == 3 and geometry:  # Polyline
                polyline_records.append({"record_id": record_id, "geometries": geometry})
                record_id += 1
            elif shape_type == 5 and geometry:  # Polygon
                polygon_records.append({"record_id": record_id, "geometries": geometry})
                record_id += 1

    return points, polyline_records, polygon_records


def transform_geometry(
    geometry: Union[Point, LineString, Polygon], from_epsg: int
) -> Union[Point, LineString, Polygon]:
    """Transform a Shapely geometry from one coordinate system to EPSG:4326."""
    if from_epsg == 4326:
        return geometry

    project = pyproj.Transformer.from_crs(
        f"EPSG:{from_epsg}", "EPSG:4326", always_xy=True
    ).transform

    transformed = transform(project, geometry)
    return cast(Union[Point, LineString, Polygon], transformed)


def get_json_response_from_shapefiles(
    shapefile_paths: List[str],
    job_names: List[str],
    category_names: List[str],
    from_epsgs: Optional[List[int]] = None,
) -> Dict:
    """Process multiple shapefiles and convert them to a JSON response.

    Args:
        shapefile_paths: List of paths to shapefiles
        job_names: List of job names corresponding to each shapefile
        category_names: List of category names corresponding to each shapefile
        from_epsgs: List of source EPSG codes (if omitted, defaults to 4326 fr each shapefile)
    """
    if len(shapefile_paths) != len(job_names) or len(shapefile_paths) != len(category_names):
        raise ValueError("Shapefile paths, job names, and category names must have the same length")

    json_response = {}

    for file_idx, shapefile_path in enumerate(shapefile_paths):
        job_name = job_names[file_idx]
        category_name = category_names[file_idx]
        from_epsg = from_epsgs[file_idx] if from_epsgs else 4326

        if job_name not in json_response:
            json_response[job_name] = {"annotations": []}

        point_records, polyline_records, polygon_records = read_shapefile(shapefile_path)

        for point_record in point_records:
            point = transform_geometry(point_record["geometry"], from_epsg)

            annotation = {
                "point": {"x": point.x, "y": point.y},
                "categories": [{"name": category_name}],
                "type": "marker",
            }

            json_response[job_name]["annotations"].append(annotation)

        for polyline_record in polyline_records:
            for line in polyline_record["geometries"]:
                transformed_line = transform_geometry(line, from_epsg)

                annotation = {
                    "polyline": [{"x": x, "y": y} for x, y in transformed_line.coords],
                    "categories": [{"name": category_name}],
                    "type": "polyline",
                }

                json_response[job_name]["annotations"].append(annotation)

        for polygon_record in polygon_records:
            record_id = polygon_record["record_id"]
            mid = f"mask-{record_id}"

            for polygon in polygon_record["geometries"]:
                transformed_polygon = transform_geometry(polygon, from_epsg)

                # Extract exterior coordinates
                exterior_points = [{"x": x, "y": y} for x, y in transformed_polygon.exterior.coords]
                bounding_poly = [{"normalizedVertices": exterior_points}]

                # Extract interior coordinates (holes)
                for interior in transformed_polygon.interiors:
                    interior_points = [{"x": x, "y": y} for x, y in interior.coords]
                    bounding_poly.append({"normalizedVertices": interior_points})

                annotation = {
                    "boundingPoly": bounding_poly,
                    "categories": [{"name": category_name}],
                    "type": "semantic",
                    "mid": mid,
                }

                json_response[job_name]["annotations"].append(annotation)

    return json_response
