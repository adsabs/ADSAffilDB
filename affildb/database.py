import os

from adsputils import load_config, setup_logging
from sqlalchemy import func


proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), "../"))
config = load_config(proj_home=proj_home)
logger = setup_logging(
    __name__,
    proj_home=proj_home,
    level=config.get("LOGGING_LEVEL", "INFO"),
    attach_stdout=config.get("LOG_STDOUT", False),
)


class DBClearTableException(Exception):
    pass


class DBWriteException(Exception):
    pass


class DBQueryException(Exception):
    pass

# general use functions, 
def clear_table(app, table):
    with app.session_scope() as session:
        try:
            session.query(table).delete()
            session.commit()
        except Exception as err:
            session.rollback()
            session.flush()
            raise DBClearTableException("Failed to clear table %s: %s" % (str(table), err))

def write_block_to_table(app, table, datablock):
    with app.session_scope() as session:
        try:
            session.execute(insert(table),datablock)
            session.commit()
        except Exception as err:
            session.rollback()
            session.flush()
            raise DBWriteException("Failed to bulk write data block: %s" % err)

def query_one_string(app, table, query_string):
    with app.session_scope() as session:
        try:
            return session.query(table.affil_id).filter_by(affil_string=query_string).all()
        except Exception as err:
            raise DBQueryException("Unable to query %s for %s: %s" % (str(table), query_string, err))


def fetch_full_table(app, table):
    with app.session_scope() as session:
        try:
            return session.query(table).all()
        except Exception as err:
            raise DBQueryException("Unable to query %s for %s: %s" % (str(table), query_string, err))


