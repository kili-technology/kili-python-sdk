# Getting started with the Kili CLI

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

Let's take an example where you want to start a project from scratch <br>
You can download ressources to run this example [here](https://storage.googleapis.com/kili-machine-learning-web/cli/CLI_Demo_Ressources.zip).<br>
Once in the current directory where all files are stored, you can run the following commands:

### Create a project

To create an IMAGE project:

```
kili project create \
            json_interface.json \
            --title "Quality inspection" \
            --input-type IMAGE \
            --description "Steel defects on production line"
```

Ouput:

```
ID                         URL
<project_id>               https://cloud.kili-technology.com/label/projects/<project_id>/
```

### List your projects

```
kili project list --max 10
```

Ouput:

```
TITLE                                ID                      PROGRESS  DESCRIPTION
Quality inspection                   <project_id>                0.0%  Steel defects on production line...
```

### Recover your project ID

```
export project_id=$(kili project list \
              | grep -m1 "Quality inspection" \
              | awk '{print $3}')
```

### Add a member to your project

```
kili project member add \
                <email_adress> \
                --project-id $project_id \
                --role REVIEWER
```

Ouput:

```
1 member(s) have been successfully added to project: <project_id>
```

### List the project's members

```
kili project member list --project-id $project_id
```

Ouput:

```
ROLE      NAME            EMAIL                ID                         ORGANIZATION
ADMIN     <your_name>     <your_email>         <your_member_id>           <your_organization>
REVIEWER  <reviewer_name> <email_adress>       <member_id>                <your_organization>
```

### Import data to your project

To import data, provide a list of files or folders (you can also procide a csv file external_id and file's paths)

```
kili project import \
    assets \
    --project-id $project_id
```

Ouput:

```
40 files have been successfully imported
```

### Import labels to your project

To import labels, provide a list of files or folders.

You can provide several paths separated by spaces.<br>
Label files are JSON files containing labels in the Kili format: the value corresponding to the
jsonResponse field of a label
(see [here](https://docs.kili-technology.com/reference/export-classification) for example). <br>
File's name must be equal to asset's external_id.<br>
In the demo folder, the labels are in a folder called ground_truths

```
kili project label \
    ground_truths \
    --project-id $project_id
```

Outputs:

```
40 labels have been successfully imported
```

If you have run a pre-annotation model, you can also import labels as predictions.
These labels will be seen as pre-annotation in the labeling interface.

```
kili project label \
    ground_truths \
    --project-id $project_id \
    --prediction \
    --model-name YOLO-run-3
```

Outputs:

```
40 labels have been successfully imported
```

### Get metrics of your project

```
kili project describe $project_id
```

Ouput:

```
Title        Quality inspection
Description  Steel defects on production line

Dataset KPIs
------------
Total number of assets      40
Number of remaining assets  10
Skipped assets              0
Progress                    25.0%

Quality KPIs
------------
Project consensus           N/A
Project honeypot            N/A
Number of reviewed assets   0
Number of open issues       0
Number of solved issues     0
Number of open questions    0
Number of solved questions  0
```
