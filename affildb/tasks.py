import html
import json
import math
import os

from kombu import Queue
from sqlalchemy import func

from affildb import app as app_module
from affildb import normalize, utils
from affildb.augmenter import AffilAugmenter as aa

import affildb.database as db

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), "../"))
app = app_module.ADSAffilDBCelery(
    "affildb-pipeline",
    proj_home=proj_home,
    config=globals().get("config", {}),
    local_config=globals().get("local_config", {}),
)
logger = app.logger

app.conf.CELERY_QUEUES = (
    Queue("augment", app.exchange, routing_key="augment"),
)

def task_augment_storage_record(app, record, norm):
    # Task receives msgs with master_pipeline.records.bib_data format
    try:
        author_data = []
        affils = record.get("aff", [])
        found = {}
        for auth in affils:
            auth = html.unescape(auth)
            alist = auth.split(";")
            author_aff = []
            for a in alist:
                if norm:
                    query_string = normalize.normalize_string(a,
                        kill_spaces = app.conf.get("NORM_KILL_SPACES", False),
                        upper_case = app.conf.get("NORM_UPPER_CASE", False)
                    )
                else:
                    query_string = normalize.clean_string(a)
                if found.get(query_string, None):
                    res = found.get(query_string)
                else:
                    res = db.query_one_string(app, query_string, norm)
                    found[query_string] = res
                author_aff.append(res)
            author_data.append(author_aff)
        augment_affil = aa().parse(record, author_data)
        return augment_affil
    except Exception as err:
        logger.error("Record affil augment failed: %s" % err)

# pipeline tasks
#@app.task(queue="augment")
def task_augment_record_bundle(records, norm=True):
    augments = []
    for rec in records:
        bibcode = rec.get("bibcode", "")
        scixID = rec.get("scix_id", "SciX:0000-abcd-9876")
        author = rec.get("author", [])
        aff = rec.get("aff", [])
        augment = {"bibcode": bibcode,
                   "scix_id": scixID,
                   "author": author,
                   "aff": aff}
        augmented = task_augment_storage_record(app, augment, norm)
        augments.append(augmented)
    # at this point, augments should contain the augment column for
    # all of the records in the bundle.  This would get sent to
    # honeycomb as a data piece for the bibcode/scixid/recordid


# only used for testing, can be deleted
def task_process_one_affil(input_string, norm=True):
    try:
        query_string = None
        if input_string:
            if norm:
                query_string = normalize.normalize_string(
                    input_string,
                    kill_spaces = app.conf.get("NORM_KILL_SPACES", False),
                    upper_case = app.conf.get("NORM_UPPER_CASE", False)
                )
            else:
                query_string = input_string
            #query and generate facets (if matched)
            result = db.query_one_string(app, query_string, norm)
            logger.info("Result for \"%s\": %s" % (input_string, result))
    except Exception as err:
        logger.error("Query failed for '%s': %s" % (input_string, err))


# data management tasks
#@app.task(queue="write-db")
def task_write_block(table, datablock):
    try:
        db.write_block_to_table(app, table, datablock)
    except Exception as err:
        logger.warning("Unable to write block to db: %s" % err)


def task_write_to_database(table_def, data):
    try:
        blocksize = app.conf.get("BLOCKSIZE", 2000)
        total_rows = len(data)
        if data and table_def:
            i = 0
            while i < total_rows:
                logger.debug(
                    "Writing to db: %s of %s rows remaining" % (len(data) - i, total_rows)
                )
                datablock = data[i : (i + blocksize)]
                insertblock = [table_def.toRow(x) for x in datablock]
                task_write_block(table_def, insertblock)
                i += blocksize
    except Exception as err:
        logger.error("Failed to write data to %s: %s" % (table_def, err))

