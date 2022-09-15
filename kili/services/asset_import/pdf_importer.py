from .base import BaseBatchImporter, BaseDataImporter, BatchParams, ProjectParams


class PdfDataImporter(BaseDataImporter):
    """
    class for importing data into a PDF project
    """

    def import_assets(self, assets):
        is_hosted = self.is_hosted_data(assets)
        project_params = ProjectParams(project_id=self.project_id, input_type=self.input_type)
        batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=False)
        batch_importer = BaseBatchImporter(self.auth, project_params, batch_params)
        result = self.import_assets_by_batch(assets, batch_importer)
        return result
