class DictClass(dict):
    def __init__(self, *args, **kwargs):
        super(DictClass, self).__init__(*args, **kwargs)
        self.__dict__ = self


class AnnotationFormat:
    Simple = 'simple'


def get_polygon(annotation):
    try:
        return annotation['boundingPoly'][0]['normalizedVertices']
    except KeyError:
        return None


def get_category(annotation):
    try:
        return annotation['categories'][0]['name']
    except KeyError:
        return None


def get_named_entity(annotation):
    try:
        return {
            'beginId': annotation['beginId'],
            'beginOffset': annotation['beginOffset'],
            'content': annotation['content'],
            'endId': annotation['endId'],
            'endOffset': annotation['endOffset']
        }
    except KeyError:
        return None


def format_image_annotation(annotation):
    category = get_category(annotation)
    polygon = get_polygon(annotation)
    named_entity = get_named_entity(annotation)
    if polygon is not None:
        return (category, polygon)
    if named_entity is not None:
        return (category, named_entity)
    if category is not None:
        return category
    return None


class Label(DictClass):
    jsonResponse = {}

    def json_response(self, format=None):
        if 'jsonResponse' not in self:
            raise Exception(
                f'You did not fetch jsonResponse for label "{self["id"] if "id" in self else self}"')
        if format is None:
            return self.jsonResponse
        if format == AnnotationFormat.Simple:
            job_names = self.jsonResponse.keys()
            if len(job_names) > 1:
                return {'error': 'Simple format is not adapted when there is more than one job. Please choose another annotation format.'}
            for job_name in job_names:
                job_response = self.jsonResponse[job_name]
                category = get_category(job_response)
                if category is not None:
                    return category
                if 'annotations' not in job_response:
                    return None
                return [format_image_annotation(annotation) for annotation in job_response['annotations']]
            return None
        raise Exception(f'format "{format}" is not a valid annotation format.')


class Asset(DictClass):
    def __init__(self, *args, **kwargs):
        super(Asset, self).__init__(*args, **kwargs)
        if 'labels' in self:
            labels = []
            for label in self['labels']:
                labels.append(Label(label))
            self.labels = labels
