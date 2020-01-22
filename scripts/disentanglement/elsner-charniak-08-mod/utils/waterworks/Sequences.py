#############
# sequences #
#############

# from http://www.hetland.org/python/distance.py
def edit_distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n
        
    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * m
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

# TODO: should be a generator
def power_set(seq):
    """Returns the power set of an (indexable) sequence."""
    return seq \
           and power_set(seq[1:]) + [seq[:1] + y for y in power_set(seq[1:])] \
           or [seq]

# TODO the following two functions should be more similar
# also, they should work the same way as the real max and min in terms
# of arguments
def maxwithundef(*args, **kw):
    """Optional keyword argument: undef.  Use this to specify an undefined 
    value.  Any argument with that value will be dropped.  If there are no
    valid arguments, undef is returned.  Default is None."""
    undef = kw.get('undef', None)
    args = [arg for arg in args if arg != undef]
    if not args:
        return undef
    elif len(args) == 1:
        return args[0]
    else:
        return max(*args)

def minwithundef(*args, **kw):
    """Optional keyword argument: undef.  Use this to specify an undefined 
    value.  Any argument with that value will be dropped.  If there are no
    valid arguments, undef is returned.  Default is None."""
    undef = kw.get('undef', None)
    args = [arg for arg in args if arg != undef]
    if not args:
        return undef
    elif len(args) == 1:
        return args[0]
    else:
        return min(*args)

def find_indices_of_unique_items(seq, sorted=True):
    """Return a pair of a list of unique indices and a hash table mapping
    nonunique indices to the first instance of it.  Unclear?  See this
    example:
    
    >>> x = [101, 102, 103, 101, 104, 106, 107, 102, 108, 109]
    >>> find_indices_of_unique_items(x)
    ([0, 1, 2, 4, 5, 6, 8, 9], {3: 0, 7: 1})"""
    vals = {} # item : index
    nonunique = {} # index : originalindex

    for index, elt in enumerate(seq):
        if elt in vals:
            originalindex = vals[elt]
            nonunique[index] = originalindex
        else:
            vals[elt] = index

    keys = vals.values()
    if sorted:
        keys.sort()

    return keys, nonunique

def separate_by_pred(pred, iterable):
    yes = []
    no = []
    for elt in iterable:
        if pred(elt):
            yes.append(elt)
        else:
            no.append(elt)
    return yes, no

def make_ranges(length, step):
    """Make non-overlapping ranges of size at most step, from 0 to length.
    Ranges are (start, end) tuples where start and end are inclusive.
    This is probably best demonstrated by example:
    >>> make_ranges(1050, 200)
    [(0, 199), (200, 399), (400, 599), (600, 799), (800, 999), (1000, 1049)]"""
    ranges = []
    count = 0
    while count < length:
        end = min(count + step, length)
        r = (count, end - 1)
        ranges.append(r)
        count += step
    return ranges

def window(seq, n=3, pad=None):
    ngram = [pad] * n
    for word in seq:
        ngram.pop(0)
        ngram.append(word)
        yield tuple(ngram)
    for x in range(n - 1):
        ngram.pop(0)
        ngram.append(pad)
        yield tuple(ngram)
