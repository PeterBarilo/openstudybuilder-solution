import json, time
import traceback
from mdr_standards_import.scripts.entities.cdisc_ct.ct_import import CTImport
from mdr_standards_import.scripts.entities.cdisc_ct.package import Package

from os import listdir, path, environ
from mdr_standards_import.scripts.exceptions.effective_date_exists import (
    EffectiveDateExists,
)
from mdr_standards_import.scripts.inconsistency_resolver import InconsistencyResolver

from mdr_standards_import.scripts.repositories.repository import (
    await_indexes,
    create_import_node,
    create_indexes_if_not_existent,
    create_ct_import,
)

NEO4J_MDR_DATABASE = environ.get("NEO4J_MDR_DATABASE", "neo4j")


def print_summary(tx, import_id, start_time):
    result = tx.run(
        """
        MATCH (import:Import) WHERE id(import) = $import_id
        CALL { WITH import
            MATCH (import)-[:INCLUDES]->()-[:CONTAINS]->(codelist)
            RETURN count(DISTINCT codelist) AS num_codelists
        }
        CALL { WITH import
            MATCH (import)-[:INCLUDES]->()-[:CONTAINS_TERM]->(term)
            RETURN count(DISTINCT term) AS num_terms
        }
       
        RETURN
            import.effective_date.year + '-'
                + right('0' + import.effective_date.month, 2)
                + '-' + right('0' + import.effective_date.day, 2)
                AS effective_date,
            size([(import)-[:HAS]->(i:Inconsistency) | i]) AS num_inconsistencies,
            size([(import)-[:HAS]->(i:ResolvedInconsistency) | i]) AS num_resolved,
            [(import)-[:INCLUDES]->(package) | package.catalogue_name] AS catalogue_names,
            num_codelists,
            num_terms
        """,
        import_id=import_id,
    ).single()

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"==")
    print(f"== Summary for the import into the CDISC DB:")
    print(f"==")
    print(f"==    # resolved inconsistencies: {result.get('num_resolved', 'n/a')}")
    print(
        f"== ! # remaining inconsistencies: {result.get('num_inconsistencies', 'n/a')}"
    )
    print(f"==")
    print(f"==      effective_date: {result.get('effective_date', 'n/a')}")
    print(f"==     catalogue names: {result.get('catalogue_names', 'n/a')}")
    print(f"==         # codelists: {result.get('num_codelists', 'n/a')}")
    print(f"==             # terms: {result.get('num_terms', 'n/a')}")
    print(f"==")
    print(f"== Duration: {round(elapsed_time, 1)} seconds")


def finish_import(tx, import_id):
    tx.run(
        """
        MATCH (import:Import) WHERE id(import) = $import_id
        REMOVE import:Running
        """,
        import_id=import_id,
    ).single()


def import_json_data_into_cdisc_db(
    effective_date,
    data_directory,
    cdisc_import_neo4j_driver,
    cdisc_import_db_name,
    author_id,
):
    """
    :param effective_date: string, the effective date in ISO 8601 format (YYYY-MM-DD)
    :param data_directory: string, the path of the directory in which the JSON files reside;
        if this is relative, it needs to be relative to the location of this script
    :param cdisc_import_neo4j_driver: the Neo4j driver instance that is used in order to connect to the Neo4j DBMS
        that holds the cdisc-import database (cf. cdisc_import_db_name);
        https://neo4j.com/docs/api/python-driver/current/api.html#neo4j.Driver
    :param cdisc_import_db_name: string, the name of the Neo4j database in which the CDISC data is loaded
        in the first place (after it will be loaded into the default MDR db)
    :param author_id: string, the id of the user that triggers this step
    """

    try:
        start_time = time.time()
        ct_import = CTImport(effective_date, author_id)

        # If using a staging database, it might not exist yet
        # so we need to create it first
        if cdisc_import_db_name != NEO4J_MDR_DATABASE:
            with cdisc_import_neo4j_driver.session(database="system") as session:
                session.run(
                    "CREATE DATABASE $database IF NOT EXISTS",
                    database=cdisc_import_db_name,
                )

        with cdisc_import_neo4j_driver.session(
            database=cdisc_import_db_name
        ) as session:
            session.write_transaction(create_indexes_if_not_existent)
            session.write_transaction(await_indexes)
            import_id = session.write_transaction(create_import_node, ct_import)

            file_names = [
                file_name
                for file_name in listdir(data_directory)
                if file_name.endswith(effective_date + ".json")
            ]
            for file_name in file_names:
                print(f"==  * Processing file: '{file_name}'.")
                with open(path.join(data_directory, file_name), "r") as package_file:
                    package = Package(ct_import)
                    package.load_from_json_data(json.load(package_file))
                    ct_import.add_package(package)

            ct_import.check_for_inconsistencies()

            inconsistency_resolver = InconsistencyResolver()
            inconsistency_resolver.resolve(ct_import)

            create_ct_import(ct_import, session)

            with session.begin_transaction() as tx:
                finish_import(tx, import_id)
                print_summary(tx, import_id, start_time)
                tx.commit()

            session.close()
    except EffectiveDateExists:
        print(
            f"== The `Import` node already exists. Skipping the import for the effective_date='{effective_date}'."
        )
    except Exception as e:
        print(f"== Exception:")
        traceback.print_exception(type(e), e, e.__traceback__)
        print(f"== Aborting the import for the effective_date='{effective_date}'.")
    finally:
        print(f"============================================")
