# Getting started with Kili CLI

## What is Kili CLI

Kili CLI has been designed to run key actions on your projects with powerful commands.
For the actions it supports, the CLI offers a more compact way to manage your projects than the Python SDK. Note that the Python SDK offers more options and may still be used for more complex project management tasks.

## Authentication

- Create and copy a [Kili API key](https://docs.kili-technology.com/docs/creating-an-api-key)
- Add the `KILI_API_KEY` variable in your bash environment (or in the settings of your favorite IDE) by pasting the API key value that you copied earlier:

  ```bash
  export KILI_API_KEY='<you api key value here>'
  ```

!!! info
    While launching commands, you can also provide you API key through the `--api-key` option. If you set your api key in the `KILI_API_KEY` environment variable and provide it once again through the `--api-key` option, Kili CLI will use the api key value provided in command options.

## Usage

The main command is `kili`. It currently has only one subcommand `project` that entails all the commands for project management :

```
kili project [COMMAND]
```

## Workflow example

Let's take an example where you want to start a project from scratch:

### Create a project

To create an IMAGE project:

```
kili project create \\
            --interface path/to/interface.json \\
            --input-type IMAGE \\
            --title "Defect detection"
            --description "Bottle defects on production line"
```

Returns:

```
Project successfully created. Id: cl4ljd3awc5gj0lpbb89nbcqg'
```

### List your projects

```
kili project list --max 10
```

Returns:

```
title                                     id                           progress  description
----------------------------------------  -------------------------  ----------  -------------------------------
Defect detection                          cl4ljd3awc5gj0lpbb89nbcqg        0.0%  Bottle defects on production...
invoice NER                               cl3d43bzb0rl71mx4580mpbt1       92.5%  For intelligent document pro...
```

### Import data to your project

To import data, provide a list of files or folders

```
kili project import \\
    reference_image.png datasets/defect_detection/ \\
    --project-id cl4ljd3awc5gj0lpbb89nbcqg \\
    --verbose
```

Returns:

```
datasets/defect_detection/visit1.mp4    SKIPPED
datasets/defect_detection/visit2.mp4    SKIPPED
Paths either do not exist, are filtered out or point towards wrong data type for the project

567 files have been successfully imported
```

### Get metrics of your project

```
kili project describe \\
    --project-id cl4ljd3awc5gj0lpbb89nbcqg \\
```

Returns:

```
Title        Defect detection
Description  Bottle defects on production line

Dataset KPIs
------------
Total number of assets      567
Number of remaining assets  82
Skipped assets              0
Progress                    14.5%

Quality KPIs
------------
Project consensus           79
Project honeypot            22
Number of reviewed assets   76
Number of open issues       5
Number of solved issues     12
Number of open questions    2
Number of solved questions  9
```
