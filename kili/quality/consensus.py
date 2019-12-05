import json
from typing import List

import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from .inter_rater import fleiss_kappa
from difflib import SequenceMatcher

from ..helper import format_result
from ..queries.asset import get_assets
from ..queries.tool import get_tools
from ..queries.project import get_project


def update_consensus_in_many_assets(client, asset_ids: List[str], consensus_marks: List[float], are_used_for_consensus: List[float]):
    asset_ids_in_string = '", "'.join(asset_ids)
    are_used_for_consensus_in_string = ', '.join(
        [str(is_used_for_consensus).lower() for is_used_for_consensus in are_used_for_consensus])
    result = client.execute('''
        mutation {
          updateConsensusInManyAssets(
            assetIDs: ["%s"],
            consensusMarks: %s
            areUsedForConsensus: [%s]
          ) {
              id
              consensusMark
              isUsedForConsensus
          }
        }
        ''' % (asset_ids_in_string, consensus_marks, are_used_for_consensus_in_string))
    return format_result('updateConsensusInManyAssets', result)


def compute_authors(labels):
    authors = []
    for label in labels:
        if label["labelType"] == "DEFAULT":
            authors.append(label["author"]["id"])
    return list(set(authors))


def compute_present_categories(asset):
    present_categories = []
    labels = asset["labels"]
    for label in labels:
        if label["labelType"] == "DEFAULT" and label["isLatestLabelForUser"]:
            response = json.loads(label["jsonResponse"])
            if "categories" not in response:
                continue
            categories = response["categories"]
            for checked_category in categories:
                present_categories.append(checked_category["name"])
    return list(set(present_categories))


def compute_bounding_polygons(labels, authors, grid_definition=100):
    all_bounding_poly = {}
    categories = []
    for author in authors:
        all_bounding_poly[author] = []
    for label in labels:
        if label["labelType"] == "DEFAULT" and label["isLatestLabelForUser"]:
            author = label["author"]["id"]
            annotations = json.loads(label["jsonResponse"])
            for annotation in annotations["annotations"]:
                multi_categories = annotation["description"][0]
                polygon_borders = []
                for border in annotation["boundingPoly"][0]["normalizedVertices"]:
                    polygon_borders.append(
                        (border['x'] * grid_definition, border['y'] * grid_definition))
                for category in multi_categories:
                    categories.append(category)
                    polygon = {"polygon": Polygon(
                        polygon_borders), "category": category}
                    all_bounding_poly[author].append(polygon)
    return all_bounding_poly, list(set(categories))


def compute_pixel_matrices_by_category(all_bounding_poly, categories, authors, grid_definition=100):
    nb_users = len(authors)
    kappa_matrices_by_category = {}
    for category in categories:
        kappa_matrices_by_category[category] = np.zeros(
            shape=(grid_definition ** 2, 2))
    for i in range(grid_definition):
        for j in range(grid_definition):
            nb_classification_for_pixel = {}
            for category in categories:
                nb_classification_for_pixel[category] = 0
            for author in authors:
                pixel_is_in_category = {}
                for category in categories:
                    pixel_is_in_category[category] = False
                for annotation in all_bounding_poly[author]:
                    polygon = annotation["polygon"]
                    if polygon.contains(Point(i, j)):
                        category = annotation["category"]
                        pixel_is_in_category[category] = True

                for category in categories:
                    if pixel_is_in_category[category]:
                        kappa_matrices_by_category[category][i *
                                                             grid_definition + j, 1] += 1
                        nb_classification_for_pixel[category] += 1

            for category in categories:
                kappa_matrices_by_category[category][i * grid_definition + j, 0] = nb_users - \
                    nb_classification_for_pixel[category]

    return kappa_matrices_by_category


def compute_consensus_for_assets(assets_for_consensus):
    consensus_by_asset = {}
    for asset in assets_for_consensus:
        categories = compute_present_categories(asset)
        dic_categories = {}
        for category in categories:
            dic_categories[category] = 0

        nb_user = 0
        labels = asset["labels"]
        for label in labels:
            if label["labelType"] == "DEFAULT" and label["isLatestLabelForUser"]:
                nb_user += 1
                response = json.loads(label["jsonResponse"])
                if "categories" not in response:
                    continue
                response_categories = response["categories"]
                for checked_category in response_categories:
                    dic_categories[checked_category["name"]] += 1
        consensus = 0
        if (nb_user - 1) == 0:
            continue
        for category in categories:
            consensus += (1.0 / (nb_user)) * dic_categories[category]
        consensus_by_asset[asset["id"]] = (1.0 / len(categories)) * consensus
    print(consensus_by_asset)
    return consensus_by_asset


def compute_consensus_for_project(client, project_id, interface_category, skip=0, first=100000):
    assets = get_assets(client, project_id, skip, first)
    if not assets:
        return None
    assets_for_consensus = []
    for asset in assets:
        if asset["isUsedForConsensus"] and (asset["status"] == "LABELED" or asset["status"] == "REVIEWED") and not \
                asset["isHoneypot"]:
            assets_for_consensus.append(asset)

    if interface_category == "IMAGE" or interface_category == "IMAGE_TO_TEXT":
        categories = list(json.loads(get_tools(client, project_id)[
            0]["jsonSettings"])["annotation_types"].keys())
        consensus_by_asset = {}
        for asset in assets_for_consensus:
            labels = asset["labels"]
            authors = compute_authors(labels)
            all_bounding_poly, categories = compute_bounding_polygons(
                labels, authors)
            kappa_matrices_by_category = compute_pixel_matrices_by_category(all_bounding_poly, categories, authors,
                                                                            grid_definition=100)

            kappa_mean_over_categories = 0
            for category in categories:
                kappa_mean_over_categories += fleiss_kappa(
                    kappa_matrices_by_category[category], method="fleiss")
                print("Asset: {}, Category: {}, Fleiss-Kappa: {}".format(asset["id"], category,
                                                                         fleiss_kappa(
                                                                             kappa_matrices_by_category[category],
                                                                             method="fleiss")))
            if len(categories) > 0:
                consensus_by_asset[asset["id"]] = max(
                    0, kappa_mean_over_categories / len(categories))
            else:
                consensus_by_asset[asset["id"]] = 0
        if interface_category == "IMAGE":
            print("Image consensus :", consensus_by_asset)
            return consensus_by_asset
        elif interface_category == "IMAGE_TO_TEXT":
            consensus_by_asset_texts = compute_consensus_for_project_ocr_texts(
                assets_for_consensus, categories)
            overall_consensus_by_asset = {}
            for id in consensus_by_asset.keys():
                overall_consensus_by_asset[id] = (
                    consensus_by_asset[id] + consensus_by_asset_texts[id]) / 2
            print("Image consensus :", consensus_by_asset)
            print("Overall consensus :", overall_consensus_by_asset)
            return overall_consensus_by_asset

    elif interface_category == "SINGLECLASS_TEXT_CLASSIFICATION" or interface_category == "MULTICLASS_TEXT_CLASSIFICATION" \
            or interface_category == "VIDEO_CLASSIFICATION":
        return compute_consensus_for_assets(assets_for_consensus)


def list_to_doubles(l):
    result = []
    for i in range(len(l)):
        for j in range(i):
            result.append((l[i], l[j]))
    return result


def compute_text_similarity_for_list_of_texts(texts, categories):
    lists = dict((cat, []) for cat in categories)
    for cat in categories:
        for text in texts:
            lists[cat].append(text[cat])
    for cat in categories:
        distances = [SequenceMatcher(None, a[0], a[1]).ratio()
                     for a in list_to_doubles(lists[cat])]
        lists[cat] = sum(distances) / \
            len(distances) if len(distances) > 0 else 0
    values = lists.values()
    return sum(values) / len(values) if len(values) > 0 else 0


def compute_consensus_for_project_ocr_texts(assets_for_consensus, categories):
    consensus_by_asset = {}
    texts_by_asset = dict.fromkeys([asset["id"]
                                    for asset in assets_for_consensus], [])
    for asset in assets_for_consensus:
        labels = [label for label in asset["labels"]
                  if label["isLatestLabelForUser"]]
        for label in labels:
            texts = dict.fromkeys(categories, "")
            annotations = json.loads(label["jsonResponse"])["annotations"]
            for annotation in annotations:
                category = list(annotation["description"][0].keys())[0]
                texts[category] = annotation["text"]
            texts_by_asset[asset["id"]].append(texts)

        consensus_by_asset[asset["id"]] = compute_text_similarity_for_list_of_texts(texts_by_asset[asset["id"]],
                                                                                    categories)
    print("Text consensus :", consensus_by_asset)
    return consensus_by_asset


def force_consensus_for_project(client, project_id: str):
    interface_category = get_project(client, project_id)['interfaceCategory']
    print(interface_category)
    consensus_by_asset = compute_consensus_for_project(
        client, project_id, interface_category)
    if not consensus_by_asset:
        return "WARNING : No asset in your project."
    asset_ids = list(consensus_by_asset.keys())
    consensus_marks = list(consensus_by_asset.values())
    are_used_for_consensus = [True for _ in consensus_marks]

    if len(asset_ids) > 0:
        update_consensus_in_many_assets(
            client, asset_ids, consensus_marks, are_used_for_consensus)
