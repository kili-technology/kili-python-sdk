from typing import List

from .base import BaseDataImporter, BatchImporter, BatchParams, ProjectParams
from .types import AssetToImport


class PdfDataImporter(BaseDataImporter):
    """
    class for importing data into a PDF project
    """

    def import_assets(self, assets: List[AssetToImport]):
        is_hosted = self.is_hosted_data(assets)
        project_params = ProjectParams(project_id=self.project_id, input_type=self.input_type)
        batch_params = BatchParams(is_hosted=is_hosted, is_asynchronous=False)
        batch_importer = BatchImporter(self.auth, project_params, batch_params)
        if not is_hosted:
            self.run_local_files_checks(assets, self.raise_error)
        result = self.import_assets_by_batch(assets, batch_importer)
        return result
