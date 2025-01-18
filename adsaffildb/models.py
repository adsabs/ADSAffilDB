try:
    from adsputils import UTCDateTime, get_date
except ImportError:
    from adsmutils import get_date, UTCDateTime

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AffilData(Base):
    """
    affil_data holds the mapping of published string and affiliation ID
    """

    __tablename__ = "affil_data"

    data_key = Column(Integer, primary_key=True, unique=True)
    affil_id = Column(String(6), nullable=False)
    affil_string = Column(Text, unique=True, nullable=False)
    created = Column(UTCDateTime, default=get_date)
    updated = Column(UTCDateTime, onupdate=get_date)


class AffilInst(Base):
    __tablename__ = "affil_inst"

    inst_key = Column(Integer, primary_key=True, unique=True)
    inst_id = Column(String(6), unique=True, nullable=False)
    inst_parents = Column(String, nullable=True)
    inst_canonical = Column(String, nullable=False)
    inst_abbreviation = Column(String, nullable=False)
    inst_country = Column(String, nullable=True)
    # in place of location, we could consider using GeoAlchemy2 here
    # especially if we can get lat-lon from ROR
    inst_location = Column(String, nullable=True)
    inst_rorid = Column(String, nullable=True)
    inst_notes = Column(Text, nullable=True)
    created = Column(UTCDateTime, default=get_date)


class AffilNorm(Base):
    __tablename__ = "affil_norm"

    norm_key = Column(Integer, primary_key=True, unique=True)
    affil_id = Column(String(6), unique=False, nullable=False)
    affil_string = Column(Text, unique=True, nullable=False)


class AffilCuration(Base):
    __tablename__ = "affil_curation"

    curation_key = Column(Integer, primary_key=True, unique=True)
    curation_count = Column(Integer, nullable=True)
    curation_id = Column(String(6), unique=False, nullable=True)
    curation_string = Column(Text, unique=True, nullable=False)
