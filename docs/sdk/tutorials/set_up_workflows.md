<!-- FILE AUTO GENERATED BY docs/utils.py DO NOT EDIT DIRECTLY -->
<a href="https://colab.research.google.com/github/kili-technology/kili-python-sdk/blob/master/recipes/set_up_workflows.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# How to set up and manage workflows with Kili

In this tutorial, we will learn how to set up basic Kili workflows:

1. Managing reviews
    1. Placing a specific percentage of project assets in the review queue
    1. Placing specific assets in the review queue
    1. Sending an asset back to the labeling queue
1. Setting up consensus
    1. Setting consensus for a specific percentage of project assets
    1. Setting consensus for specific assets to compute consensus KPIs
1. Setting up honeypot
1. Assigning labelers to assets
1. Prioritizing assets in the labeling queue

To work with this notebook, you will have to install and instantiate Kili.


```python
!pip install kili
```


```python
from kili.client import Kili
import getpass
import os
```


```python
if "KILI_API_KEY" not in os.environ:
    KILI_API_KEY = getpass.getpass("Please enter your API key: ")
else:
    KILI_API_KEY = os.environ["KILI_API_KEY"]
```


```python
kili = Kili(
    api_key=KILI_API_KEY,  # not needed if KILI_API_KEY is already in environment variables
    # api_endpoint="https://cloud.kili-technology.com/api/label/v2/graphql",
    # the line above can be uncommented and changed if you are working with an on-premise version of Kili
)
```


```python
project_id = "<YOUR PROJECT ID>"
```

For information on how to set up a Kili project, refer to the [basic project setup](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/basic_project_setup/) tutorial.

## Managing reviews

### Placing a specific percentage of project assets in the review queue

You can set up the percentage of assets that will automatically appear in the review queue (1-100%).


```python
kili.update_properties_in_project(project_id=project_id, review_coverage=50)
```




    {'id': 'cld95dpne0n2y0joi6wuq3u6v', 'reviewCoverage': 50}



## Setting up consensus

Consensus works by having more than one labeler annotate the same asset. When the asset is labeled, a consensus score is calculated to measure the agreement level between the different annotations for a given asset.
This is a key measure for controlling label production quality.

To set up consensus, you will need to have at least two project members.
For information on how to add users and assign them to your project, refer to the [basic project setup](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/basic_project_setup/) tutorial.

### Setting consensus for a specific percentage of project assets

Let's set the percentage of the project dataset that will be annotated several times, to enable consensus calculations. We will also set the minimum number of labelers to label each one of these assets.


```python
def set_consensus_coverage(project_id: str, consensus_tot_coverage: int, min_consensus_size: int):
    kili.update_properties_in_project(
        project_id=project_id,
        consensus_tot_coverage=consensus_tot_coverage,
        min_consensus_size=min_consensus_size,
    )


set_consensus_coverage(project_id=project_id, consensus_tot_coverage=50, min_consensus_size=3)
```

### Setting consensus for specific assets to compute consensus KPIs

You can manually select specific project assets to be used for computing consensus KPIs.


```python
def set_assets_for_consensus(project_id: str, external_ids: list):
    kili.update_properties_in_assets(
        project_id=project_id,
        external_ids=external_ids,
        is_used_for_consensus_array=[True] * len(external_ids),
    )


external_ids = ["1.jpg", "2.jpg", "3.jpg"]
set_assets_for_consensus(project_id=project_id, external_ids=external_ids)
```

For more information on consensus, refer to our [documentation](https://docs.kili-technology.com/docs/consensus-overview).

## Setting up honeypot

Honeypot (or __gold standard__) is a tool for auditing the work of labelers by measuring the accuracy of their annotations.
Honeypot works by interspersing assets with defined ground truth label in the annotation queue. This way you can measure the agreement level between your ground truth and the annotations made by labelers.

You can manually select specific project assets to be used as honeypots.


```python
asset_external_id = "1.jpg"
json_response = {"JOB_0": {"categories": [{"confidence": 100, "name": "OBJECT_B"}]}}

kili.create_honeypot(
    project_id=project_id, asset_external_id=asset_external_id, json_response=json_response
);
```

For more information on honeypot, refer to our [documentation](https://docs.kili-technology.com/docs/consensus-overview).

## Assigning labelers to assets

You can assign specific labelers to specific assets in your project. You can do that by assigning users' emails to the selected asset IDs. Remember that you can assign more than one user to a specific asset.


```python
def assign_labelers_to_assets(project_id: str, external_ids: list, to_be_labeled_by_array: list):
    kili.update_properties_in_assets(
        project_id=project_id,
        external_ids=external_ids,
        to_be_labeled_by_array=to_be_labeled_by_array,
    )


external_ids = ["1.jpg", "2.jpg", "3.jpg"]
to_be_labeled_by_array = [
    ["example1@example.com"],
    ["example2@example.com"],
    ["example3@example.com"],
]

assign_labelers_to_assets(
    project_id=project_id, external_ids=external_ids, to_be_labeled_by_array=to_be_labeled_by_array
)
```

The `to_be_labeled_by_array` argument is a list of lists. Each of the sub-lists can contain several e-mails. This way you can assign several labelers to one asset.

For example:

`to_be_labeled_by_array = [["example1@example.com"], ["example1@example.com", "example2@example.com"], ["example3@example.com"]]`

For information on how to add users and assign them to your project, refer to the [basic project setup](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/basic_project_setup/) tutorial.
For information on assigning assets to users, refer to our [documentation](https://docs.kili-technology.com/docs/queue-prioritization).

## Prioritizing assets in the labeling queue

If you have certain assets that you need to have labeled earlier or later than the rest, you can use Kili's asset prioritization methods.


```python
def set_priority_for_assets(project_id: str, external_ids: list, priorities: list):
    kili.update_properties_in_assets(
        project_id=project_id, external_ids=external_ids, priorities=priorities
    )


external_ids = ["1.jpg", "2.jpg", "3.jpg"]
priorities = [1, 5, 10]
set_priority_for_assets(project_id=project_id, external_ids=external_ids, priorities=priorities)
```

For information on setting asset priorities, refer to our [documentation](https://docs.kili-technology.com/docs/queue-prioritization).

### Placing specific assets in the review queue

When done with your basic workflow setup, you can place specific, labeled assets in the review queue.
As this requires the assets to be labeled, first, let's simulate adding labels to some of our assets.
The method will return the list of newly-added label IDs.


```python
json_response_array = [
    {"JOB_0": {"categories": [{"confidence": 100, "name": "OBJECT_B"}]}} for i in range(3)
]
kili.append_labels(
    project_id=project_id,
    asset_external_id_array=["1.jpg", "2.jpg", "3.jpg"],
    json_response_array=json_response_array,
    label_type="DEFAULT",
)
```






    [{'id': 'cld95duf80o3k0jpa5f8bdolk'},
     {'id': 'cld95duf80o3l0jpa6tkv947s'},
     {'id': 'cld95duf90o3m0jpaccwo0awt'}]



Now, let's place some assets in the review queue. The method will return a project ID and a list of asset IDs placed in the review queue.


```python
external_ids = ["1.jpg", "2.jpg", "3.jpg"]
kili.add_to_review(project_id=project_id, external_ids=external_ids)
```

For more information on asset statuses, refer to our [documentation](https://docs.kili-technology.com/docs/asset-lifecycle).

### Sending an asset back to the labeling queue

You can also send specific labeled assets back to the labeling queue.
asset_names, first, let's simulate adding labels to some of our assets.
The method will return the list of newly-added label IDs.


```python
json_response_array = [{"JOB_0": {"categories": [{"confidence": 100, "name": "OBJECT_B"}]}}] * 3
kili.append_labels(
    project_id=project_id,
    asset_external_id_array=["1.jpg", "2.jpg", "3.jpg"],
    json_response_array=json_response_array,
    label_type="DEFAULT",
)
```






    [{'id': 'cld95dy130iss0ko864g7c7hr'},
     {'id': 'cld95dy130ist0ko8fgokak6h'},
     {'id': 'cld95dy130isu0ko8gb0s1ckc'}]



Now, we will send some of our assets back to the labeling queue. The method will return a project ID and a list of asset IDs that were sent back to the labeling queue.


```python
external_ids = ["1.jpg", "2.jpg", "3.jpg"]
kili.send_back_to_queue(project_id=project_id, external_ids=external_ids)
```




    {'id': 'cld95dpne0n2y0joi6wuq3u6v',
     'asset_ids': ['cld95dq340006wvszexj8u1uh',
      'cld95dq340007wvszoxdhet57',
      'cld95dq340008wvszveinxcy2']}



For more information on asset statuses, refer to our [documentation](https://docs.kili-technology.com/docs/asset-lifecycle).

## Summary

Done!

We have learned how to handle the review workflow, set up consensus and honeypot in a project, assign specific labelers to specific assets, and how to prioritize assets in the labeling queue.