import html
import re


class FixSemicolonsException(Exception):
    pass


class CleanStringException(Exception):
    pass


class NormalizeStringException(Exception):
    pass


class BatchNormalizeException(Exception):
    pass


regex_norm_semicolon = re.compile(r";\s*;")
regex_norm_punct = re.compile(r"[-!?.|,;:/\\]")
regex_norm_spaces = re.compile(r"\s+")


# BEGIN utils also used by ADSAffilPipeline
def fix_semicolons(string):
    try:
        string_x = regex_norm_semicolon.sub(";", string).strip()
        if string_x != string:
            return fix_semicolons(string_x)
        else:
            return string_x
    except Exception as err:
        raise FixSemicolonsException("Error in fix_semicolons: %s" % err)


def clean_string(string):
    try:
        string = html.unescape(string)
        string = fix_semicolons(string)
        string = string.strip(";").strip()
        return string
    except Exception as err:
        raise CleanStringException("Error in clean_string: %s" % err)


def normalize_string(string, kill_spaces=False, upper_case=False):
    # normalizing consists of
    # 1) removing all spaces and other punctuation with re
    # 2) converting all ascii chars to upper-case
    try:
        string = regex_norm_punct.sub(" ", string)
        string = " ".join(string.split())
        string = clean_string(string)
        if upper_case:
            string = string.upper()
        if kill_spaces:
            string = regex_norm_spaces.sub("", string)
        return string
    except Exception as err:
        raise NormalizeStringException("Error in normalize_string: %s" % err)


def normalize_block(data):
    try:
        output = []
        conflicts = {}
        failures = ()
        seen = {}
        for rec in data:
            oldstring = rec[1]
            if oldstring:
                try:
                    newstring = normalize_string(oldstring)
                except Exception as err:
                    failures.append({"aff_id": rec[0],
                                     "aff_string": rec[1],
                                     "error": err})
                if not seen.get(newstring, None):
                    output.append({"affil_id": rec[0], "affil_string": newstring})
                    seen[newstring] = [rec[0]]
                else:
                    if rec[0] not in seen.get(newstring, []):
                        seen[newstring].append(rec[0])
        for k,v in seen.items():
            if len(v) > 1:
                conflicts[k] = v
        return (output, conflicts, failures)
    except Exception as err:
        raise BatchNormalizeException("Failed to normalize batch: %s" % err)
