# Plugins library

## Context

In this section you can find multiple examples of use-cases where our system of plugins can help you in the Kili projects.

You can also refer to our [tutorial](./plugins_development.md) to develop your plugin and iterate on it locally, before uploading the final version to Kili.

For further information concerning the Kili plugins, refer to the [Reference page](../plugins.md)

## Library of pre-built plugins

In the folder [`plugins_library`](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/plugins_library){target=_blank} you can find multiple examples of plugins that are ready to use in your projects. They can be split in various use-cases:

### 1. Programmatic QA
One application of plugins is to automate your quality checks: you can directly write your business rules in a Python script and upload them to Kili to have each new label automatically checked.

### 1.1 Image Object Detection example

Let's imagine a project where we want to process images and detect some objects. One of the jobs is to detect an object and we are sure that in any image of the dataset we can have at most a single object of that type. In order to be sure that we will have only one object in all submitted labels, we can create a plugin that, in case a label has 2 BBoxes for that type of objects, will automatically create an issue with a clear instruction and will send the label back to the queue.
z
- Plugin file: [`plugin_image.py`](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/plugins_library/plugin_image.py){target=_blank}
- End-to-end notebook showcasing this example: [`plugins_example.ipynb`](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/plugins_example.ipynb){target=_blank}

### 1.2 Document processing example

Let's imagine another project where we process invoices. The project has two jobs and several transcription tasks associated with them. One of the jobs is about payment information and must contain a proper IBAN number as well as currency. The IBAN must start with FR, and the currency should be one of: *EURO* or *DOLLAR*. Kili's interface customization options are powerful and flexible, but won't help us in this specific situation so we have to turn to Kili plugins for help. We'll set up our Kili plugin to check these two rules when labelers click *Submit*. If the annotations don't match our predefined rules, our QA bot will add issues to the asset and send the asset back to the labeling queue. At the end, our script will calculate labeling accuracy and insert the accuracy metric in the json_metadata of the asset. All that with no need to engage a human reviewer.

- Plugin file: [`plugin_document.py`](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/plugins_library/plugin_document.py){target=_blank}
- End-to-end notebook showcasing this example: [`plugins_example_document.ipynb`](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/plugins_example_document.ipynb){target=_blank}

### 2. Consensus resolution

When working with consensus for object detection tasks, it is often handy for a reviewer to access the annotations of all the labelers involved, compare them and choose the best one. With Kili plugins, this task will be much simpler.

For example: you can program your plugin to create an additional annotation that combines the annotations created by all the labelers. This way, you can instantaneously get a big-picture overview and only act when the situation calls for it. In large projects, this can save you a significant amount of time.

- Plugin file: [`plugin_consensus.py`](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/plugins_library/plugin_consensus.py){target=_blank}

### 3. Parallel labeling

For projects with specialized workforce, you can split your workforce in several groups, with each of them focused on a specific portion of your labeling tasks. For instance, group A (experts in the A domain) only does labeling for job A and group B (experts in the B domain) only does labeling for job B. With Kili Plugins, you could then combine these workflows by aggregating the annotations done by multiple labelers as one label. Your reviewers would then be presented with the combined results.

- Plugin file: [`parallel_labeling_plugin.py`](https://github.com/kili-technology/kili-python-sdk/blob/master/recipes/plugins_library/parallel_labeling_plugin.py){target=_blank}
