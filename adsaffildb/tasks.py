import json
import math
import os

from kombu import Queue
from sqlalchemy import func

from adsaffildb import app as app_module
from adsaffildb import normalize, utils
from adsaffildb.models import AffilData as affil_data
from adsaffildb.models import AffilNorm as affil_norm

import adsaffildb.database as db

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), "../"))
app = app_module.ADSAffilDBCelery(
    "affildb-pipeline",
    proj_home=proj_home,
    config=globals().get("config", {}),
    local_config=globals().get("local_config", {}),
)
logger = app.logger

app.conf.CELERY_QUEUES = (
    Queue("normalize", app.exchange, routing_key="normalize"),
    Queue("augment", app.exchange, routing_key="augment"),
)

@app.task(queue="augment")
def task_query_one_affil(input_string, normalize=True):
    try:
        query_string = None
        table = None
        if input_string:
            if normalize:
                query_string = normalize.normalize_string(
                    input_string,
                    kill_spaces = app.conf.get("NORM_KILL_SPACES", False),
                    upper_case = app.conf.get("NORM_UPPER_CASE", False)
                )
                table = app.conf.get("NORMALIZED_DATA_TABLE", None)
            else:
                query_string = input_string
                table = app.conf.get("RAW_DATA_TABLE", None)
        if query_string and table:
            return db.query_one_string(app, table, query_string)
        else:
            return
    except Exception as err:
        logger.error("Query failed for '%s': %s" % (str(input_string),err))
        return
                    

@app.task(queue="normalize")
def task_process_block(data):
    try:
        (norm_data, conflicts, failures) = normalize.normalize_block(data)
        if norm_data:
            db.write_block_to_table(app, affil_norm, norm_data)
        else:
            logger.warning("Normalize.normalize_block returned no data!")
    except Exception as err:
        logger.error("Normalize block failed! %s" % err)

def task_normalize_all():
    try:
        db.clear_table(app, affil_norm)
    except Exception as err:
        logger.error("Failed to clear affil_norm table: %s" % err)
    else:
        logger.debug("Affil_norm table has been cleared.")
        try:
            result = db.fetch_full_table(app, affil_data)
            logger.debug("Affil_data table has been fetched.")
            if result:
                blocksize = app.conf.get("BLOCKSIZE", 1000)
                total_rows = len(result)
                i = 0
                while i < total_rows:
                    logger.debug(
                        "Writing to db: %s of %s rows remaining" % 
                            (len(data) - i, total_rows)
                    )
                    processblock = result[i : (i + blocksize)]
                    tasks.task_process_block.delay(processblock)
                    i += blocksize
        except Exception as err:
            logger.error("Failed to normalize affil_data table: %s" % err)
        else:
            logger.info("affil_data has been normalized in affil_norm")
