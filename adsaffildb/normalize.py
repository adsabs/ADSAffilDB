import html
import re

regex_norm_semicolon = re.compile(r";\s*;")
regex_norm_punct = re.compile(r'[-!?.,;:/\\]')

# BEGIN utils also used by ADSAffilPipeline
def fix_semicolons(string):
    try:    
        string_x = regex_norm_semicolon.sub(';', string).strip()
        if string_x != string:
            return fix_semicolons(string_x)
        else:       
            return string_x
    except Exception as err:
        raise FixSemicolonsException('Error in fix_semicolons: %s' % err)
                    
def clean_string(string):
    try:
        string = html.unescape(string)
        string = fix_semicolons(string)
        string = string.strip(';').strip()
        return string
    except Exception as err:
        raise CleanStringException('Error in clean_string: %s' % err)

def normalize_string(string):
    # normalizing consists of
    # 1) removing all spaces and other punctuation with re
    # 2) converting all ascii chars to upper-case
    try:
        string = regex_norm_punct.sub(' ', string)
        string = ' '.join(string.split())
        string = string.upper()
        return string
    except Exception as err:
        raise NormalizeStringException('Error in normalize_string: %s' % err)
