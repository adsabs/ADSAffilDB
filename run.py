import argparse
import os
from affildb import utils, normalize, tasks
from adsputils import load_config, setup_logging

from affildb.models import AffilInst as affil_inst
from affildb.models import AffilData as affil_data

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), "./"))
config = load_config(proj_home=proj_home)

logger = setup_logging("affildb", level=config.get("LOGGING_LEVEL", "WARN"), proj_home=proj_home, attach_stdout=config.get("LOG_STDOUT", "FALSE"))

def get_args():

    parser = argparse.ArgumentParser("Affiliations curation and management")

    parser.add_argument("-ld",
                        "--load-db",
                        dest="load_db",
                        action="store_true",
                        default=False,
                        help="Load parent_child relations and matched affiliation strings from .tsv files")

    parser.add_argument("-lp",
                        "--load-pc",
                        dest="load_pc",
                        action="store_true",
                        default=False,
                        help="Load parent_child relations from .tsv file.")

    parser.add_argument("-la",
                        "--load-affs",
                        dest="load_affs",
                        action="store_true",
                        default=False,
                        help="Load matched affiliation strings from .tsv file.")

    parser.add_argument("-n",
                        "--norm",
                        dest="norm",
                        action="store_true",
                        default=config.get("NORM_AFFILS", True),
                        help="Generate normalized version of affil_data")

    parser.add_argument("-d",
                        "--debug",
                        dest="debug",
                        action="store_true",
                        default=False,
                        help="Run the debug string 'Bartol / University of Delaware' through pipeline")

    parser.add_argument("-t",
                        "--test",
                        dest="test",
                        action="store_true",
                        default=False,
                        help="Run the test record bib data through pipeline (2025ApJ...978..126Z)")

    return parser.parse_args()

def main():

    args = get_args()

    if args.debug:
        testString = "Bartol / University of Delaware"
        tasks.task_process_one_affil(testString)

    elif args.test:
        try:
            testfiles = [
                "./tests/stubdata/2025ApJ...978..126Z_bibdata.json",
                "./tests/stubdata/2024PhRvL.132b1803A.json"]
            records = []
            for f in testfiles:
                with open(f, "r") as fi:
                    records.append(json.load(fi))
            tasks.task_augment_record_bundle(records)
        except Exception as err:
            print("failed: %s" % err)

    if args.load_db:
        args.load_pc = True
        args.load_affs = True

    if args.load_pc:
        infile = config.get("COUNTRY_PARENT_CHILD_FILE", "./data/cpc.tsv")
        with_header = True
        delimiter = config.get("DELIMITER", "\t")
        dataParentChild = utils.read_flat_files(infile,
                                                with_header,
                                                delimiter)
        uniqueParentChild = utils.merge_parents(dataParentChild)
        tasks.task_write_to_database(affil_inst, uniqueParentChild)

    if args.load_affs:
        infile = config.get("MATCHED_AFFILS_FILE", "./data/Affils.tsv")
        with_header = False
        delimiter = config.get("DELIMITER", "\t")
        dataMatchedAffils = utils.read_flat_files(infile,
                                                  with_header,
                                                  delimiter)
        dataNormAffils = []
        for row in dataMatchedAffils:
            affil_id = row[0]
            affil_string = row[1]
            if args.norm:
                norm_string = normalize.normalize_string(
                    affil_string,
                    kill_spaces = config.get("NORM_KILL_SPACES", False),
                    upper_case = config.get("NORM_UPPER_CASE", False)
                )
            else:
                norm_string = normalize.clean_string(
                    affil_string
                )
            outrow = [affil_id, affil_string, norm_string]
            dataNormAffils.append(outrow)
        if dataNormAffils:
            tasks.task_write_to_database(affil_data, dataNormAffils)


if __name__ == '__main__':
    main()
