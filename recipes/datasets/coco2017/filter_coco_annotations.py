import json

image_ids_to_keep = {
    397133,
    37777,
    252219,
    87038,
    174482,
    403385,
    6818,
    480985,
    458054,
    331352,
}

instances_val2017 = json.load(open("instances_val2017.json"))

instances_val2017_filtered = {}
instances_val2017_filtered["info"] = instances_val2017["info"]
instances_val2017_filtered["licenses"] = instances_val2017["licenses"]
instances_val2017_filtered["categories"] = instances_val2017["categories"]
instances_val2017_filtered["images"] = [
    img for img in instances_val2017["images"] if img["id"] in image_ids_to_keep
]
instances_val2017_filtered["annotations"] = [
    ann for ann in instances_val2017["annotations"] if ann["image_id"] in image_ids_to_keep
]

with open("instances_val2017_filtered.json", "w") as f:
    json.dump(instances_val2017_filtered, f)


captions_val2017 = json.load(open("captions_val2017.json"))

captions_val2017_filtered = {}
captions_val2017_filtered["info"] = captions_val2017["info"]
captions_val2017_filtered["licenses"] = captions_val2017["licenses"]
captions_val2017_filtered["images"] = [
    img for img in captions_val2017["images"] if img["id"] in image_ids_to_keep
]
captions_val2017_filtered["annotations"] = [
    ann for ann in captions_val2017["annotations"] if ann["image_id"] in image_ids_to_keep
]

with open("captions_val2017_filtered.json", "w") as f:
    json.dump(captions_val2017_filtered, f)

person_keypoints_val2017 = json.load(open("person_keypoints_val2017.json"))

person_keypoints_val2017_filtered = {}
person_keypoints_val2017_filtered["info"] = person_keypoints_val2017["info"]
person_keypoints_val2017_filtered["licenses"] = person_keypoints_val2017["licenses"]
person_keypoints_val2017_filtered["categories"] = person_keypoints_val2017["categories"]
person_keypoints_val2017_filtered["images"] = [
    img for img in person_keypoints_val2017["images"] if img["id"] in image_ids_to_keep
]
person_keypoints_val2017_filtered["annotations"] = [
    ann for ann in person_keypoints_val2017["annotations"] if ann["image_id"] in image_ids_to_keep
]

with open("person_keypoints_val2017_filtered.json", "w") as f:
    json.dump(person_keypoints_val2017_filtered, f)
