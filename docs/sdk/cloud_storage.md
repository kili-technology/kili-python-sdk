# Cloud storage module

!!! warning "Alpha feature"
    The cloud storage feature is currently in alpha. It is still under active development: methods and behaviors can still evolve until the feature is complete.

!!! info "Cloud Storage Integration and Connection"
    A cloud storage integration is a connection between a Kili organization and a cloud storage (AWS, GCP or Azure).
    Once a cloud storage integration is created, it can be used in any project of the organization.
    Adding a cloud storage integration from the SDK is currently not supported.
    More information about how to create a cloud storage integration can be found [here](https://docs.kili-technology.com/docs/adding-assets-to-project#creating-a-remote-storage-integration).

    A cloud storage connection is a cloud storage integration used in a Kili project.
    It is used to import data from a cloud storage to a project.
    More information about how to use a cloud storage integration in a project can be found [here](https://docs.kili-technology.com/docs/adding-assets-to-project#adding-assets-located-in-remote-storage-integration).

!!! info "Azure"
    It is recommended to install the Azure dependencies to use the Azure cloud storage integration and connection.
    ```bash
    pip install kili[azure]
    ```

## Queries

::: kili.entrypoints.queries.data_integration.__init__.QueriesDataIntegration
::: kili.entrypoints.queries.data_connection.__init__.QueriesDataConnection

## Mutations

:::kili.entrypoints.mutations.data_connection.__init__.MutationsDataConnection
