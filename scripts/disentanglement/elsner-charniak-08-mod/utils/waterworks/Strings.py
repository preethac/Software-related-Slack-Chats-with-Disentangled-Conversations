###################
# parsing helpers #
###################

def try_parse_int(val, default=None):
    """Attempt to parse a string as an integer.  If parsing fails,
    the default will be returned."""
    try:
        return int(val)
    except ValueError:
        return default

def try_parse_float(val, default=None):
    """Attempt to parse a string as an integer.  If parsing fails,
    we try again as a float.  If parsing fails again, the default will
    be returned."""
    try:
        return int(val)
    except ValueError:
        try:
            return float(val)
        except ValueError:
            return default

def try_parse_date(val, default=None):
    """Attempt to parse a string as an date.  If parsing fails in
    recoverable way, as much information about the date as possible will
    be returned.  If the input is not parsable at all, the default will
    be returned."""
    import mx.DateTime
    try:
        return mx.DateTime.Parser.DateTimeFromString(val)
    except:
        return default

def multisplit(string_to_split, delimiters):
    """Example:

    >>> print multisplit('hello there, how are you?', delimiters=',')
    ['hello there', ' how are you?']
    >>> print multisplit('hello there, how are you?', delimiters=', ')
    ['hello', 'there', 'how', 'are', 'you?']
    """
    import re
    splitter_re = re.compile('|'.join(["(?:%s)" % delimiter 
        for delimiter in delimiters]))
    splitted = splitter_re.split(string_to_split)
    return [splittee for splittee in splitted 
        if splittee and splittee not in delimiters]

###########
# strings #
###########

def zfill_by_num(x, num_to_fill_to):
    """zfill with an example, i.e. give it a number of the length (string
    length) you want it to fill to.

    >>> zfill_by_num(1, 102)
    '001'
    """
    l = len(str(num_to_fill_to))
    return str(x).zfill(l)

def pretty_time_range(diff, show_seconds=True):
    """Given a number of seconds, returns a string attempting to represent
    it as shortly as possible.
    
    >>> pretty_time_range(1)
    '1s'
    >>> pretty_time_range(10)
    '10s'
    >>> pretty_time_range(100)
    '1m40s'
    >>> pretty_time_range(1000)
    '16m40s'
    >>> pretty_time_range(10000)
    '2h46m40s'
    >>> pretty_time_range(100000)
    '1d3h46m40s'
    """
    diff = int(diff)
    days, diff = divmod(diff, 86400)
    hours, diff = divmod(diff, 3600)
    minutes, seconds = divmod(diff, 60)
    str = ''
    if days: 
        str += '%sd' % days
    if hours: 
        str += '%sh' % hours
    if minutes: 
        str += '%sm' % minutes
    if show_seconds and seconds: 
        str += '%ss' % seconds
    if not str:
        if show_seconds: str = '%ss' % seconds
        else: str = '0m'
    return str
