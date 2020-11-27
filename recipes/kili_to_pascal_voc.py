"""
This python script shows a function to convert your kili exported response to a pascal VOC .xml file
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
import numpy as np

response = {'JOB_0': {'annotations': [{'boundingPoly': [{'normalizedVertices': [{'x': 0.5559003685448103,
                                                                                 'y': 0.4574172704456453},
                                                                                {'x': 0.5559003685448103,
                                                                                    'y': 0.16874512185265989},
                                                                                {'x': 0.8007011034682624,
                                                                                    'y': 0.16874512185265989},
                                                                                {'x': 0.8007011034682624, 'y': 0.4574172704456453}]}],
                                       'categories': [{'name': 'OBJECT_A', 'confidence': 100}],
                                       'mid': '2020112712200780-59247',
                                       'score': None,
                                       'type': 'rectangle'},
                                      {'boundingPoly': [{'normalizedVertices': [{'x': 0.32129966424316886,
                                                                                 'y': 0.6690094212467863},
                                                                                {'x': 0.32129966424316886,
                                                                                 'y': 0.34859845003362977},
                                                                                {'x': 0.6205005624829435,
                                                                                 'y': 0.34859845003362977},
                                                                                {'x': 0.6205005624829435, 'y': 0.6690094212467863}]}],
                                       'categories': [{'name': 'OBJECT_A', 'confidence': 100}],
                                       'mid': '2020112712200870-40716',
                                       'score': None,
                                       'type': 'rectangle'},
                                      {'boundingPoly': [{'normalizedVertices': [{'x': 0.17084921257146393,
                                                                                 'y': 0.16421100433549252},
                                                                                {'x': 0.17084921257146393,
                                                                                 'y': 0.11433571164665213},
                                                                                {'x': 0.3297996897613443,
                                                                                 'y': 0.11433571164665213},
                                                                                {'x': 0.3297996897613443, 'y': 0.16421100433549252}]}],
                                       'categories': [{'name': 'OBJECT_B', 'confidence': 100}],
                                       'mid': '2020112712201112-20149',
                                       'score': None,
                                       'type': 'rectangle'}]}}


def parse_annotations(response, xml_label, width, height):
    for _, job_response in response.items():
        if 'annotations' in job_response:
            annotations = job_response['annotations']
            for annotation in annotations:
                vertices = annotation['boundingPoly'][0]['normalizedVertices']
                categories = annotation['categories']
                for category in categories:
                    annotation_category = ET.SubElement(xml_label, 'object')
                    name = ET.SubElement(annotation_category, 'name')
                    name.text = category['name']
                    pose = ET.SubElement(annotation_category, 'pose')
                    pose.text = 'Unspecified'
                    truncated = ET.SubElement(annotation_category, 'truncated')
                    truncated.text = '0'
                    difficult = ET.SubElement(annotation_category, 'difficult')
                    difficult.text = '0'
                    occluded = ET.SubElement(annotation_category, 'occluded')
                    occluded.text = '0'
                    bndbox = ET.SubElement(annotation_category, 'bndbox')
                    x_vertices = [int(np.round(v['x'] * width))
                                  for v in vertices]
                    y_vertices = [int(np.round(v['y'] * height))
                                  for v in vertices]
                    xmin = ET.SubElement(bndbox, 'xmin')
                    xmin.text = str(min(x_vertices))
                    xmax = ET.SubElement(bndbox, 'xmax')
                    xmax.text = str(max(x_vertices))
                    ymin = ET.SubElement(bndbox, 'ymin')
                    ymin.text = str(min(y_vertices))
                    ymax = ET.SubElement(bndbox, 'ymax')
                    ymax.text = str(max(y_vertices))


def provide_voc_headers(xml_label, width, height, parameters={}):
    folder = ET.SubElement(xml_label, 'folder')
    folder.text = parameters.get('folder', '')

    filename = ET.SubElement(xml_label, 'filename')
    filename.text = parameters.get('filename', '')

    path = ET.SubElement(xml_label, 'path')
    path.text = parameters.get('path', '')

    source = ET.SubElement(xml_label, 'source')
    database = ET.SubElement(source, 'database')
    database.text = 'Kili Technology'

    size = ET.SubElement(xml_label, 'size')
    width_xml = ET.SubElement(size, 'width')
    width_xml.text = str(width)
    height_xml = ET.SubElement(size, 'height')
    height_xml.text = str(height)
    depth = ET.SubElement(size, 'depth')
    depth.text = parameters.get('depth', '3')

    segmented = ET.SubElement(xml_label, 'segmented')
    segmented.text = 0


def transform_kili_response_to_pascal_voc(response, output_file, width, height, parameters={}):
    xml_label = ET.Element('annotation')

    provide_voc_headers(xml_label, width, height, parameters=parameters)

    parse_annotations(response, xml_label, width, height)

    xmlstr = minidom.parseString(ET.tostring(
        xml_label)).toprettyxml(indent="   ")
    with open(output_file, "w") as f:
        f.write(xmlstr)


def main():
    parameters = {
        'filename': 'file_001.png'
    }
    output_file = './examples/voc_label.xml'
    width = 1920
    height = 1080
    transform_kili_response_to_pascal_voc(
        response, output_file, width, height, parameters)
    with open(output_file, 'r') as f:
        print(f.read())


if __name__ == '__main__':
    main()
