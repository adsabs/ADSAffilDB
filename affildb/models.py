try:
    from adsputils import UTCDateTime, get_date
except ImportError:
    from adsmutils import get_date, UTCDateTime

from sqlalchemy import Column, Integer, String, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AffilInst(Base):
    __tablename__ = "affil_inst"

    inst_key = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    inst_id = Column(String(6), primary_key=True, unique=True, nullable=False)
    inst_parents = Column(String, nullable=True)
    inst_canonical = Column(String, nullable=False)
    inst_abbreviation = Column(String, nullable=False)
    inst_country = Column(String, nullable=False)
    inst_iso_country = Column(String, nullable=False)
    # in place of location, we could consider using GeoAlchemy2 here
    # especially if we can get lat-lon from ROR
    inst_location = Column(String, nullable=True)
    inst_rorid = Column(String, nullable=True)
    inst_notes = Column(Text, nullable=True)
    created = Column(UTCDateTime, default=get_date)
    updated = Column(UTCDateTime, onupdate=get_date)

    def toJSON(self):
        try:
            outputJson = {"inst_iso_country": self.inst_iso_country,
                          "inst_country": self.inst_iso_country,
                          "inst_parents": self.inst_parents,
                          "inst_id": self.inst_id,
                          "inst_abbreviation": self.inst_abbreviation,
                          "inst_canonical": self.inst_canonical,
                          "error": ""}
            return outputJson
        except Exception as err:
            return {"error": err}
                
    def toRow(rowdat):
        if len(rowdat) == 6:
            return {"inst_iso_country": rowdat[0],
                    "inst_country": rowdat[1],
                    "inst_parents": rowdat[2],
                    "inst_id": rowdat[3],
                    "inst_abbreviation": rowdat[4],
                    "inst_canonical": rowdat[5]}
        else:
            return {}
        
class AffilData(Base):
    """
    affil_data holds the mapping of published string and affiliation ID
    """

    __tablename__ = "affil_data"

    data_key = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    affil_id = Column(String(6), primary_key=True, unique=False, nullable=False)
    affil_string = Column(Text, unique=True, nullable=False)
    norm_string = Column(Text, primary_key=True, unique=False, nullable=False)
    flagged = Column(Boolean, default=False, nullable=False)
    created = Column(UTCDateTime, default=get_date, nullable=False)
    updated = Column(UTCDateTime, onupdate=get_date, nullable=False)

    __table_args__ = (Index('norm_index', norm_string, postgresql_using="hash"),)

    def toJSON(self):
        try:
            outputJSON = {"affil_id": self.affil_id,
                          "affil_string": self.affil_string,
                          "norm_string": self.norm_string}
            return outputJSON
        except Exception as err:
            return {"error": err}

    def toRow(rowdat):
        if len(rowdat) == 3:
            return {"affil_id": rowdat[0],
                    "affil_string": rowdat[1],
                    "norm_string": rowdat[2]}
        else:
            return {}
