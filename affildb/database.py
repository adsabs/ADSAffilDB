import os

from adsputils import load_config, setup_logging
from affildb.models import AffilInst as affil_inst
from affildb.models import AffilData as affil_data
from affildb.augmenter import AffilAugmenter as aa

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

# db management functions,
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

def fetch_data_table(app, table):
    with app.session_scope() as session:
        try:
            results = session.query(table).all()
            raw_data = []
            for row in results:
                raw_data.append([row.affil_id, row.affil_string])
            return raw_data
        except Exception as err:
            raise DBQueryException("Unable to query %s for %s: %s" % (str(table), query_string, err))


def query_distinct_norm(app, table):
    with app.session_scope() as session:
        try:
            return session.query(table).distinct(table.norm_string).all()
        except Exception as err:
            raise DBQueryException("Unable to query %s for distinct normalized strings: %s" % (str(table), err))


# augment pipeline functions
def query_one_string(app, query_string, norm):
    with app.session_scope() as session:
        outputDefault = {}
        try:
            inst_id = None
            if norm:
                inst_id = session.query(affil_inst).join(affil_data, affil_data.affil_id == affil_inst.inst_id).filter(affil_data.norm_string==query_string).first()
            else:
                inst_id = session.query(affil_inst).join(affil_data, affil_data.affil_id == affil_inst.inst_id).filter(affil_data.affil_string==query_string).first()

            if not inst_id:
                return outputDefault

            else:
                child_data = inst_id.toJSON()
                parent_str = child_data.get("inst_parents", "")
                parent_data = []
                if parent_str:
                    parent_id_list = [x.strip() for x in parent_str.split(";")]
                    for p in parent_id_list:
                        try:
                            pdata = session.query(affil_inst).filter(affil_inst.inst_id==p).first().toJSON()
                            parent_data.append(pdata)
                        except Exception as err:
                            print("This shouldn't happen: %s" % err)
                child_data["parent_data"] = parent_data
                return child_data

        except Exception as err:
            raise DBQueryException("Unable to query %s for %s: %s" % (str(affil_data), query_string, err))


def augment_record(app, record, norm):
    try:
        author_data = []
        for auth in record.get("aff", []):
            alist = auth.split(";")
            author_aff = []
            for a in alist:
                author_aff.append(query_one_string(app, a.strip(), norm))
            author_data.append(author_aff)
        augment_affil = aa().parse(author_data)
        return augment_affil
    except Exception as err:
        print("Welp... %s" % err)
        

# output is...
#{'inst_country': 'USA', 'inst_parents': 'A00976', 'inst_id': 'A00977', 'inst_abbreviation': 'Bartol Res Inst', 'inst_canonical': 'University of Delaware, Bartol Research Institute', 'error': '', 'parent_data': [{'inst_country': 'USA', 'inst_parents': '', 'inst_id': 'A00976', 'inst_abbreviation': 'U Delaware', 'inst_canonical': 'University of Delaware', 'error': ''}]}
