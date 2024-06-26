<!-- FILE AUTO GENERATED BY docs/utils.py DO NOT EDIT DIRECTLY -->
<a href="https://colab.research.google.com/github/kili-technology/kili-python-sdk/blob/main/recipes/basic_project_setup.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# How to set up a basic Kili project

In this tutorial, we will learn how to set up a basic Kili project.

Here are the steps that we will follow:

1. Installing and instantiating Kili
2. Creating a basic Kili project
3. Adding assets to project
4. Adding users to project

## Installing and instantiating Kili

First, let's install and import the required modules.


```python
%pip install kili
```


```python
from kili.client import Kili
```

Now, let's set up variables needed to create an instance of the Kili object.

We will need your API key and Kili's API endpoint.

If you are unsure how to look up your API key, refer to [https://docs.kili-technology.com/docs/creating-an-api-key](https://docs.kili-technology.com/docs/creating-an-api-key).


```python
kili = Kili(
    # api_endpoint="https://cloud.kili-technology.com/api/label/v2/graphql",
    # the line above can be uncommented and changed if you are working with an on-premise version of Kili
)
```

## Creating a basic Kili project

To create a Kili project, you must first set up its interface.

We will create a simple image project with just one simple classification job and two categories: `OBJECT_A` and `OBJECT_B`.

To learn more about Kili project interfaces, refer to [https://docs.kili-technology.com/docs/customizing-project-interface](https://docs.kili-technology.com/docs/customizing-project-interface).


```python
interface = {
    "jobs": {
        "JOB_0": {
            "mlTask": "CLASSIFICATION",
            "required": 1,
            "isChild": False,
            "content": {
                "categories": {"OBJECT_A": {"name": "Object A"}, "OBJECT_B": {"name": "Object B"}},
                "input": "radio",
            },
        }
    }
}

result = kili.create_project(
    title="[Kili SDK Notebook]: Basic Project Setup",
    description="Project Description",
    input_type="IMAGE",
    json_interface=interface,
)
```

For further processing, we will need to find out what our project ID is.

We can easily retrieve it from the project creation response message:


```python
project_id = result["id"]
print("Project ID: ", project_id)
```

    Project ID:  clcun99cn15wx0lq4c15a4dj7


Now, let's add some assets to be labeled.

We will use some free off-the-shelf examples from the Internet.

## Adding assets to project


```python
# Image urls
url1 = "https://storage.googleapis.com/label-public-staging/car/car_2.jpg"
url2 = "https://storage.googleapis.com/label-public-staging/car/car_1.jpg"
url3 = "https://storage.googleapis.com/label-public-staging/recipes/inference/black_car.jpg"

assets = kili.append_many_to_dataset(
    project_id=project_id,
    content_array=[url1, url2, url3],
    external_id_array=["image_1", "image_2", "image_3"],
)
```

## Adding users to project

Now we need to add users to our project. Before we do that, we have to add them to our organization. **Note that you have to be an org admin to be able to do that**.

For more info on roles in an organization, refer to [https://docs.kili-technology.com/docs/user-roles-in-organization](https://docs.kili-technology.com/docs/user-roles-in-organization).


```python
firstname = "Jane"
lastname = "Doe"
email = "no.such.email@no.such.domain.com"
password = "12345"
organization_role = "USER"

from kili.exceptions import GraphQLError

try:
    kili.create_user(email, password, organization_role, firstname, lastname)
except GraphQLError as err:
    print(str(err))
```

    error: "[noOrganizationRights] You cannot use this function because it seems that you do not have access to this organization. Please contact you organization admin. -- This can be due to: User isn't admin from the organization | trace : false"


If you already have users in your organization, here's how you can easily access their IDs:

1) First, retrieve your organization ID:


```python
org_id = kili.organizations()[0]["id"]
```

2) Then, based on your org ID, retrieve the full list of org users, with their e-mails:


```python
all_org_users = kili.users(organization_id=org_id)

all_emails = [i["email"] for i in all_org_users]
```

3) We will use the e-mail of the new user to add our new user to our project:


```python
user = kili.append_to_roles(project_id, "no.such.email@no.such.domain.com", role="LABELER")
print(user)
```

    {'user': {'id': 'clcumy1fx15ci0lre0k21fnu7', 'email': 'no.such.email@no.such.domain.com'}, 'role': 'LABELER'}


## Cleanup

We can remove the project that we created:


```python
kili.delete_project(project_id)
```

## Summary

Done. We've successfully set up a Kili project, defined its interface, created a brand new user, and finally added our new user to the new project. Well done!
