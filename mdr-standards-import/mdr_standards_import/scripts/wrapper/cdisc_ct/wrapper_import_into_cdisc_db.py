"""
This script serves as the entry point for the pipeline step 'Import CDISC CT into CDISC DB'.

This script is meant to be called e.g. via:

> `python -m pipenv run import_cdisc_ct_into_cdisc_db <user initials> <JSON directory name>`

The script expects the following parameters:

1. <user initials> - The username of the person who started the process: String, e.g. "MT", "TKQT", ...
2. <JSON directory name> - Optional, default "". The directory name where the JSON files are stored. It can be absolute or relative.
    If relative (or empty), the passed directory name will be appended to the content of the environment variable 'CDISC_DATA_DIR'.
    String, E.g. "", "subset-1", "/my/absoulte/path/to/json-files"
"""

from os import environ

from mdr_standards_import.scripts.import_scripts.cdisc_ct.import_json_data_into_cdisc_db import (
    import_json_data_into_cdisc_db,
)
from mdr_standards_import.scripts.utils import (
    get_directory_name,
    get_author_id,
    get_cdisc_neo4j_driver,
    get_ordered_package_dates,
)


CDISC_IMPORT_DATABASE = environ.get("NEO4J_CDISC_IMPORT_DATABASE", "cdisc")


def wrapper_import_cdisc_ct_into_cdisc_db(
    author_id: str, json_data_directory: str = ""
):
    """
    Calls the import step to transform the JSON files into the CDISC CT graph structure.
    """
    cdisc_neo4j_driver = get_cdisc_neo4j_driver()

    package_dates = get_ordered_package_dates(json_data_directory)
    print(f"Found the following dates: {str(package_dates)}")
    for effective_date in package_dates:
        print(f"============================================")
        print(
            f"== Importing JSON data into the cdisc-DB='{CDISC_IMPORT_DATABASE}' for the effective_date='{effective_date}'."
        )
        print(f"==")
        import_json_data_into_cdisc_db(
            effective_date,
            json_data_directory,
            cdisc_neo4j_driver,
            CDISC_IMPORT_DATABASE,
            author_id,
        )

    cdisc_neo4j_driver.close()


if __name__ == "__main__":
    wrapper_import_cdisc_ct_into_cdisc_db(get_author_id(1), get_directory_name(2, "cdisc_ct"))
