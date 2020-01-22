from __future__ import nested_scopes
import sys

class ondemand(property):
    """A property that is loaded once from a function."""
    def __init__(self, fget, doc=None):
        property.__init__(self, fget=self.get, fdel=self.delete, doc=doc)
        self.loadfunc = fget
        import weakref
        self.values = weakref.WeakKeyDictionary()
    def get(self, obj):
        if obj not in self.values:
            self.load(obj)
        return self.values[obj]
    def load(self, obj):
        self.values[obj] = self.loadfunc(obj)
    def delete(self, obj):
        # XXX this may not be needed any more
        try:
            del self.values[obj]
        except:
            pass

def initialize(ob, args):
    """In __init__, call initialize(self, locals()) to load all passed 
    arguments."""
    if 'self' in args:
        del args['self']
    for k, v in args.items():
        setattr(ob, k, v)

def make_attributes_from_args(*argnames):
    """
    This function simulates the effect of running
      self.foo = foo
    for each of the given argument names ('foo' in the example just
    now). Now you can write:
        def __init__(self,foo,bar,baz):
            make_attributes_from_args('foo','bar','baz')
            ...
    instead of:
        def __init__(self,foo,bar,baz):
            self.foo = foo
            self.bar = bar
            self.baz = baz
            ... 
    """
    callerlocals = sys._getframe(1).f_locals
    callerself = callerlocals['self']
    for a in argnames:
        try:
            setattr(callerself,a,callerlocals[a])
        except KeyError:
            raise KeyError, "Function has no argument '%s'" % a

def make_dict_from_args(*argnames):
    """
    The sequel to the best selling make_attributes_from_args!  Turn your
    arguments into a dictionary.  Takes a list of the names of the arguements
    to convert, returns a dictionary with their names : values.

    def some_function(foo, bar, qux):
        d = make_dict_from_args('foo', 'bar', 'qux')

    d is now:
    { 'foo' : value_of_foo, 'bar' : value_of_bar, 'qux' : value_of_qux }
    """
    callerlocals=sys._getframe(1).f_locals
    d = {}
    for a in argnames:
        try:
            d[a] = callerlocals[a]
        except KeyError:
            raise KeyError, "Function has no argument '%s'" % a
    return d

def dumpobj(o, double_underscores=0):
    """Prints all the object's non-callable attributes.  If double_underscores
    is false, it will skip attributes that begin with double underscores."""
    print repr(o)
    for a in [x for x in dir(o) if not callable(getattr(o, x))]:
        if not double_underscores and a.startswith("__"):
            continue
        try:
            print "  %20s: %s " % (a, getattr(o, a))
        except:
            pass
    print ""

_count = 0 # certainly not thread safe
def trace(func, stream=sys.stdout):
    """Good old fashioned Lisp-style tracing.  Example usage:
    
    >>> def f(a, b, c=3):
    >>>     print a, b, c
    >>>     return a + b
    >>>
    >>>
    >>> f = trace(f)
    >>> f(1, 2)
    |>> f called args: [1, 2]
    1 2 3
    <<| f returned 3
    3

    TODO: print out default keywords (maybe)"""
    name = func.func_name
    global _count
    def tracer(*args, **kw):
        global _count
        s = ('\t' * _count) + '|>> %s called with' % name
        _count += 1
        if args:
            s += ' args: %r' % list(args)
        if kw:
            s += ' kw: %r' % kw
        print >>stream, s
        ret = func(*args, **kw)
        _count -= 1
        print >>stream, ('\t' * _count) + '<<| %s returned %s' % (name, ret)
        return ret
    return tracer

def get_current_traceback_tuple():
    """Returns a semiformatted traceback of the current exception as a tuple
    in this form:
       (exceptionclass, exceptioninstance, lines_of_string_traceback_lines)"""
    import traceback
    exceptionclass, exceptioninstance, tb = sys.exc_info()
    tb_lines = traceback.format_tb(tb)
    return (exceptionclass, exceptioninstance, tb_lines)

class Symbol:
    """Lisp symbols for Python (sort of).  These are like strings but
    used differently (think exception classes vs. string exceptions).
    Two symbols of the same name are equal but not equal to the string
    of their name, i.e. Symbol('x') == Symbol('x'), but Symbol('x') !=
    'x'."""
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.name)
    def __eq__(self, other):
        return self.name == other.name

def generic_repr(self):
    """Generic representation -- prints out the object's dictionary,
    ignoring keys that start with '_' and values that are non-false.

    Example usage:
    class A:
        def __init__(self, *whatever):
            do_things()

        __repr__ = generic_repr
    """
    d = ', '.join('%s=%r' % item 
        for item in sorted(self.__dict__.items()) 
        if not item[0].startswith('_') and item[1])
    name = str(self.__class__).replace('__main__.', '')
    return "%s(%s)" % (name, d)
