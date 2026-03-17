
import csv

class ReadPCFileException(Exception):
    pass


def read_flat_files(infile=None, with_header=True, delimiter="\t"):
    allData = []
    try:
        with open(infile, "r") as fpc:
            csv.QUOTE_ALL
            fileReader = csv.reader(fpc, delimiter=delimiter, quoting=csv.QUOTE_NONE)
            allData = [rowData for rowData in fileReader]

        if allData:
            if with_header:
                headerRow = allData[0]
                allData = allData[1:]
            else:
                headerRow = []
            return allData
        else:
            raise Exception("No data read from file %s" % infile)
    except Exception as err:
        raise ReadPCFileException("%s" % str(err))


def merge_parents(parentChildData):
    if parentChildData:
        pcdict = {}
        for row in parentChildData:
            child = row[3]
            parent = row[2]
            if parent:
                if pcdict.get(child, None):
                    pcdict[child].append(parent)
                else:
                    pcdict[child] = [parent]
                row[1] = ''
        uniqued = []
        seen = {}
        for row in parentChildData:
            child = row[3]
            if not seen.get(child, None):
                if pcdict.get(child, None):
                    row[2] = "; ".join(pcdict[child])
                uniqued.append(row)
                seen[child] = 1
        return uniqued
