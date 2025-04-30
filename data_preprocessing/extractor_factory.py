import os
from .data_extractor import DataExtractor
from .disease_extractor import DiseaseExtractor
from .disease_detail_extractor import DetailDiseaseExtractor

"""Use of Factory to Pick the Right Extractor"""


def get_extractor_for_file(file_path, output_dir):
    """
    Returns the appropriate extractor instance based on file name
    """
    filename = os.path.basename(file_path).lower()

    # If it's a disease PDF file(for exemple diag_code_infection.pdf)
    if ".pdf" in filename:
        return DiseaseExtractor(output_dir=output_dir)
    if ".xml" in filename:  # case of detail's disease
        return DetailDiseaseExtractor(output_dir=output_dir)
    # Else fallback to the generic extractor
    return DataExtractor(output_dir=output_dir)
