import json
import os

from adsputils import load_config, setup_logging

proj_home = os.path.realpath(os.path.dirname(__file__))
config = load_config(proj_home=proj_home)
logger = setup_logging(
    "run.py",
    proj_home=proj_home,
    level=config.get("LOGGING_LEVEL", "INFO"),
    attach_stdout=config.get("LOG_STDOUT", False),
)


class AffIdDictException(Exception):
    pass


class MatchDictException(Exception):
    pass


def read_match_dict(filename=None):
    try:
        matchMap = []
        with open(filename, "r") as fd:
            for line in fd.readlines():
                matchData = line.strip().split("\t")
                if len(matchData) != 2:
                    logger.warning("Bad line in %s: %s" % (filename, line.strip()))
                else:
                    match = {"data_id": matchData[0], "data_pubstring": matchData[1]}
                    matchMap.append(match)
        return matchMap
    except Exception as err:
        raise MatchDictException(
            "Could not read curated match dictionary, %s: %s" % (filename, err)
        )


def read_affid_dict(filename=None):
    try:
        affIdDict = {}
        affIdMap = []
        with open(filename, "r") as fd:
            for line in fd.readlines():
                affIdData = line.rstrip().split("\t")
                if len(affIdData) != 5:
                    print(line)
                country = affIdData[0]
                parentId = affIdData[1]
                affId = affIdData[2]
                abbrev = affIdData[3]
                canonical = affIdData[4]
                if not affIdDict.get(affId, None):
                    affIdDict[affId] = {
                        "inst_country": country,
                        "inst_parents": [parentId],
                        "inst_abbreviation": abbrev,
                        "inst_canonical": canonical,
                    }
                else:
                    current = affIdDict.get(affId)
                    current["inst_parents"].append(parentId)
                    affIdDict[affId] = current
        if affIdDict:
            for k, v in affIdDict.items():
                rec = {**v}
                rec["inst_parents"] = json.dumps(rec["inst_parents"])
                rec.setdefault("inst_id", k)
                affIdMap.append(rec)
        return affIdMap
    except Exception as err:
        raise AffIdDictException("Could not read affil id dictionary: %s" % err)
