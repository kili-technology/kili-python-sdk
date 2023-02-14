# Plugins library

## Context

In this section you can find multiple examples of use-cases where our system of plugins can help you in the Kili projects.

You can refer to our [tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/plugins_development/) to develop your plugin and iterate on it locally (or use the [plugins_development.ipynb](../plugins_development.ipynb) notebook), before uploading the final version to Kili.

If you want to see some end-to-end example of our plugins, you can refer to the notebooks [plugins_example.ipynb](../plugins_example.ipynb) (example of a plugin checking the number of annotation) and [plugins_example_document.ipynb](../plugins_example_document.ipynb) (example of a plugin checking some document processing rules).

For further information concerning the Kili plugins, refer to our [Documentation](https://python-sdk-docs.kili-technology.com/latest/sdk/plugins/)

## Library of pre-built plugins

In this folder you can find multiple examples of plugins that are ready to use in your projects. They can be split in various use-cases:

### 1. Programmatic QA
One application of plugins is to automate your quality checks: you can directly write your business rules in a Python script and upload them to Kili to have each new label automatically checked.
### 1.1 Image Object Detection

Let's imagine a project where we want to process images and detect some objects. One of the jobs is to detect an object and we are sure that in any image of the dataset we can have at most a single object of that type. In order to be sure that we will have only one object in all submitted labels, we can create a plugin that, in case a label has 2 BBoxes for that type of objects, will automatically create an issue with a clear instruction and will send the label back to the queue.

- Plugin file: `plugin_image.py`
- End-to-end notebook showcasing this example: `plugins_example.ipynb`

### 1.2 Document processing

Let's imagine another project where we process invoices. The project has two jobs and several transcription tasks associated with them. One of the jobs is about payment information and must contain a proper IBAN number as well as currency. The IBAN must start with FR, and the currency should be one of: *EURO* or *DOLLAR*. Kili's interface customization options are powerful and flexible, but won't help us in this specific situation so we have to turn to Kili plugins for help. We'll set up our Kili plugin to check these two rules when labelers click *Submit*. If the annotations don't match our predefined rules, our QA bot will add issues to the asset and send the asset back to the labeling queue. At the end, our script will calculate labeling accuracy and insert the accuracy metric in the json_metadata of the asset. All that with no need to engage a human reviewer.

- Plugin file: `plugin_document.py`
- End-to-end notebook showcasing this example: `plugins_example_document.ipynb`
### 2. Consensus resolution:

When working with consensus for object detection tasks, it is often handy for a reviewer to access the annotations of all the labelers involved, compare them and choose the best one. With Kili plugins, this task will be much simpler.

For example: you can program your plugin to create an additional annotation that combines the annotations created by all the labelers. This way, you can instantaneously get a big-picture overview and only act when the situation calls for it. In large projects, this can save you a significant amount of time.

- Plugin file: `plugin_consensus.py`
### 3. Parallel labeling

For projects with specialized workforce, you can split your workforce in several groups, with each of them focused on a specific portion of your labeling tasks. For instance, group A (experts in the A domain) only does labeling for job A and group B (experts in the B domain) only does labeling for job B. With Kili Plugins, you could then combine these workflows by aggregating the annotations done by multiple labelers as one label. Your reviewers would then be presented with the combined results.

- Plugin file: `parallel_labeling_plugin.py`
