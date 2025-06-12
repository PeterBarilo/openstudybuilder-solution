
from os import path

from mdr_standards_import.scripts.utils import (
    get_ordered_package_dates,
)
from mdr_standards_import.scripts.wrapper.cdisc_ct.wrapper_import_into_cdisc_db import (
    wrapper_import_cdisc_ct_into_cdisc_db,
)
from mdr_standards_import.scripts.wrapper.cdisc_ct.wrapper_import_from_cdisc_db_into_mdr import (
    wrapper_import_cdisc_ct_from_cdisc_db_into_mdr,
)
from mdr_standards_import.scripts.wrapper.cdisc_data_models.wrapper_import_into_cdisc_db import (
    wrapper_import_cdisc_data_models_into_cdisc_db,
)
from mdr_standards_import.scripts.wrapper.cdisc_data_models.wrapper_import_from_cdisc_db_into_mdr import (
    wrapper_import_cdisc_data_models_from_cdisc_db_into_mdr,
)


def bulk_import(
    author_id: str, json_data_directory: str = "", import_ct: bool = True, import_data_models: bool = True
):
    # Import into CDISC db
    # CDISC CT
    if import_ct:
        wrapper_import_cdisc_ct_into_cdisc_db(
            author_id, path.join(json_data_directory, "cdisc_ct")
        )

    # CDISC Data models
    if import_data_models:
        wrapper_import_cdisc_data_models_into_cdisc_db(
            author_id, path.join(json_data_directory, "cdisc_data_models")
        )

    # Import from CDISC db into MDR db
    # CDISC CT
    if import_ct:
        package_dates = get_ordered_package_dates(
            path.join(json_data_directory, "cdisc_ct")
        )
        for effective_date in package_dates:
            wrapper_import_cdisc_ct_from_cdisc_db_into_mdr(
                author_id=author_id, effective_date=effective_date
            )

    # CDISC Data models
    if import_data_models:
        wrapper_import_cdisc_data_models_from_cdisc_db_into_mdr(
            author_id=author_id, json_data_directory=json_data_directory
        )
