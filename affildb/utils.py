
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

