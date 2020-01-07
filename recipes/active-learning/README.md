# Using Active Learning to scale your annotation project

Using Active Learning to select the data instances to label may allow you to achieve better performance with less manual work. Kili API offers you the capability to add a priority index on your assets to label the most important ones first.

The script attached gives you a few hints on how to leverage active learning with Kili, but feel free to personalize it to better fit your needs.

## Connecting to Kili

First use the class `ActiveLearner` defined in the attached script to connect to the API.

```python
active_learner = ActiveLearner(
    args.email, 
    args.password, 
    args.api_endpoint, 
    args.project_id
)
```

## Using the ActiveLearner class

The ActiveLearner exposes 3 important methods:
* `active_learner.get_assets_to_evaluate()`: will get you all the assets that have not been labelled yet.
* `active_learner.prioritize_assets(to_evaluate_assets, scorer)`: takes the assets you got with the previous functions, and a `scorer` method (of your choice) which will be needed to rank your assets following your Active Learning algorithm decisions. It should return a sorted list of assets (according to your scorer function). Please note we expect the scorer to give a score conveying how important it is to label the asset (so if your active learning rule is to choose the assets for which a given model is less confident, simply provide as scorer an inverse of your model confidence).
* `active_learner.update_assets_priority(ranked_assets)`: sends back the assets to Kili and update the priority field in Kili so that you can label the most important ones first.


