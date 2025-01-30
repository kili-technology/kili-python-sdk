# Tutorials

Welcome to the Kili Tutorials Homepage!

We understand that getting started with a new product can sometimes be challenging. That's why we have created this page to provide you with easy-to-follow tutorials that will help you understand how to use the Kili Python SDK in no time.

Here is a brief overview of our tutorials:

## Basic project setup

In [this tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/basic_project_setup/) you will learn how to set up a new project in Kili, configure its settings, and add assets and users to it.

## Importing assets

[This tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/importing_assets_and_metadata/) will show you how to import assets into your Kili project and add asset metadata.

Because videos and Rich Text assets may be more complex to import, we’ve created separate tutorials devoted to them:

- For video assets, refer to [this tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/importing_video_assets/).
- For rich text assets, see [here](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/import_text_assets).
- For PDF assets, see [here](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/importing_pdf_assets).
- For Geosat multi-layer assets, see [here](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/importing_multilayer_geosat_assets).

## Importing labels

In [this tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/importing_labels/) you will learn how to import different types of label formats supported by Kili, including model-based pre-annotations and pre-existing labels from other projects.

[This tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/ner_pre_annotations_openai/) explains how to use a powerful OpenAI Large Language Model (LLM) to generate pre-annotations, which will then be imported into a Named Entity Recognition (NER) Kili project.

For other specific use cases, see these tutorials:

- [Importing OCR pre-annotations](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/ocr_pre_annotations/)
- [Importing segmentation pre-annotations](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/pixel_level_masks/)
- [Importing DINOv2 classification pre-annotations](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/finetuning_dinov2/)

Additionally, we’ve devoted one [tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/inference_labels/) to explaining the most common use cases for importing and using model-generated labels: actively monitoring the quality of a model currently deployed to production to detect issues like data drift, and using a model to speed up the process of label creation.

## Working with labels

In this section, you’ll learn the various ways you can process labels with Kili.

[This tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/medical_imaging/) shows you how to upload medical images to Kili using pydicom, upload dicom tags as metadata to your assets, download segmentation labels from Kili, and finally convert them to Numpy masks for visualization with matplotlib.

The [Tagtog to Kili](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/tagtog_to_kili/) tutorial will show you how to convert and import your tagtog assets and labels into Kili.

The label parsing [tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/label_parsing/) will show you how you can read and write label data more efficiently.

This [tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/importing_coco/) shows how to import COCO annotations into Kili.

This [tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/importing_pascalvoc/) shows how to import PascalVOC annotations into Kili.

On this [tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/geojson/), you will learn how to import GeoJSON annotations into Kili, and how to export Kili annotations to GeoJSON.

## Managing workflows

In [this tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/set_up_workflows/) you will learn how to manage your review queue, set up quality assurance measures, assign specific labelers to assets, and prioritize assets to be annotated.

## Exporting Project Data

[This tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/export_a_kili_project/) will show you how to export your project’s assets and labels to different formats supported by Kili.

## Plugins

A plugin is a custom Python script uploaded to Kili and triggered by an event that you define. For instance, you can trigger a specific action when a labeler clicks on Submit.

In [this tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/plugins_development/) you will learn how to create your own custom plugins.

[Here](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/plugins_library/), you’ll find example use cases for using Kili plugins.

For a more specific use case, follow [this tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/plugins_example/) on how to set up and use Kili plugins to monitor the quality of labels added to your project in real-time, without having to involve human reviewers.

Webhooks are really similar to plugins, except they are self-hosted, and require a web service deployed at your end, callable by Kili. To learn how to use webhooks, follow [this tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/webhooks_example/).

## LLM

[This tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/llm_static/) explains how to import conversations into a Kili project to annotate responses generated by a Large Language Model (LLM).

[This tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/llm_dynamic/) guides you through setting up a Kili project with an integrated LLM. You'll learn how to create and link the LLM model to the project and initiate a conversation using the Kili SDK.


## Integrations

[This tutorial](https://python-sdk-docs.kili-technology.com/latest/sdk/tutorials/vertex_ai_automl_od/) will show you how train an object detection model with Vertex AI AutoML and Kili for faster annotation

## More

For more tutorials and recipes, see our [Github repository](https://github.com/kili-technology/kili-python-sdk/tree/main/recipes).
