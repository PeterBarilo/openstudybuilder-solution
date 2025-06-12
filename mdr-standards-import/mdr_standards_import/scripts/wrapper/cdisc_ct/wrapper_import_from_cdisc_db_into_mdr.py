"""
This script serves as the entry point for the pipeline step 'Import CT from CDISC DB into MDR DB'.

It is meant to be called e.g. via:

> `python -m pipenv run import_ct_from_cdisc_db_into_mdr <user initials> <effective date>`

The script expects the following parameters:

1. <user initials> - The username of the person who started the process: String, e.g. "MT", "TKQT", ...
2. <effective date> - The CDISC effective date to be imported.
"""

from os import environ
from mdr_standards_import.scripts.import_scripts.cdisc_ct.import_into_mdr_db import (
    import_from_cdisc_db_into_mdr,
)
from mdr_standards_import.scripts.utils import (
    get_effective_date,
    get_author_id,
    get_cdisc_neo4j_driver,
    get_mdr_neo4j_driver,
)


CDISC_IMPORT_DATABASE = environ.get("NEO4J_CDISC_IMPORT_DATABASE", "cdisc")
MDR_DATABASE = environ.get("NEO4J_MDR_DATABASE", "neo4j")


def wrapper_import_cdisc_ct_from_cdisc_db_into_mdr(
    author_id: str, effective_date: str
):
    cdisc_neo4j_driver = get_cdisc_neo4j_driver()
    mdr_neo4j_driver = get_mdr_neo4j_driver()

    print(f"============================================")
    print(
        f"== Importing from the cdisc-DB='{CDISC_IMPORT_DATABASE}' into the MDR-DB='{MDR_DATABASE}' for the effective_date='{effective_date}'..."
    )
    print(f"==")
    import_from_cdisc_db_into_mdr(
        effective_date,
        cdisc_neo4j_driver,
        CDISC_IMPORT_DATABASE,
        mdr_neo4j_driver,
        MDR_DATABASE,
        author_id,
    )

    mdr_neo4j_driver.close()
    cdisc_neo4j_driver.close()


if __name__ == "__main__":
    wrapper_import_cdisc_ct_from_cdisc_db_into_mdr(get_author_id(1), get_effective_date(2))
