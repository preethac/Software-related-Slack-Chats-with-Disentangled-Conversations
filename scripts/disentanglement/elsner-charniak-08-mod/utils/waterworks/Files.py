from __future__ import nested_scopes
import os, sys, pipes
from gzip import GzipFile

#########
# files #
#########

def is_filelike(obj, modes_needed='rw'):
    """Returns whether obj has some of the necessary methods for a
    file object.  modes_needed is a string of modes to check for ('r',
    'w', or 'rw')."""
    try:
        if 'r' in modes_needed:
            obj.read
        if 'w' in modes_needed:
            obj.write
            obj.flush
            obj.close
    except AttributeError:
        return False
    else:
        return True

def filename_from_obj(obj):
    """Attempts to recover the filename from an object (a string, file
    object, etc.)"""
    if isinstance(obj, basestring):
        return obj
    else:
        try:
            return obj.filename
        except AttributeError:
            pass
        try:
            return obj.name # file objects
        except AttributeError:
            pass
    return obj

def open_file_or_filename(obj, mode='r'):
    """obj can be a file-like object or a string of a filename.  Returns a
    file or file-like object associated with obj."""
    if is_filelike(obj, modes_needed=mode):
        return obj
    elif isinstance(obj, basestring):
        return possibly_compressed_file(obj, mode)
    else:
        raise TypeError("Can't make a file out of %r." % obj)

def sortedfile(filename, mode='r', sortcmd='sort -n'):
    """Returns a file-like object which contains a sorted version of
    filename.  Note that the file-like object returned is a 
    NamedTemporaryFile and will be deleted when it goes out of scope."""
    import pipes, tempfile
    tf = tempfile.NamedTemporaryFile()

    t = pipes.Template()
    t.append(sortcmd, '--')
    t.copy(filename, tf.name)

    return tf

# TODO: write mode is broken when the file doesn't exist yet
def possibly_compressed_file(filename, mode='r'):
    from bz2 import BZ2File
    # normalize the filename
    filename = filename.replace('.gz', '')
    filename = filename.replace('.bz2', '')
    gzip_name = "%s.gz" % filename
    bzip_name = "%s.bz2" % filename
    if os.path.exists(filename):
        return file(filename, mode)
    elif os.path.exists(gzip_name): # try adding .gz and using GzipFile
        return GzipFile(gzip_name, mode)
    elif os.path.exists(bzip_name): # try adding .bz2 and using BZ2File
        return BZ2File(bzip_name, mode)
    else:
        raise IOError("Can't find file (or compressed version): '%s'" % \
            filename)

def read_file_with_timeout(fileobject, timeout=1):
    """Given a fileobject, we try to read from it.  If it takes longer than
    timeout to read, we raise an IOError."""
    # this is taken from the examples in the documentation for the
    # signal module
    import signal

    def handler(signum, frame):
        raise IOError("Couldn't read from file object within %s seconds" % \
            timeout)

    # Set the signal handler and an alarm to go off
    # TODO: save the old signal handler!
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
    result = fileobject.read()
    signal.alarm(0) # Disable the alarm
    # TODO: restore the old signal handler!
    return result

def linecountinfile(file_or_filename):
    """Count the lines in a file, requires us to read the entire file."""
    f = open_file_or_filename(file_or_filename)
    numlines = 0
    for line in f:
        numlines += 1
    f.close()
    return numlines

def mkdirparents(path):
    """Python version of the shell command "mkdir -p".  Won't raise an
    exception if the path already exists.  os.makedirs() will raise an
    exception (this may be a bug)."""
    try:
        os.makedirs(path)
    except OSError, oe:
        pass

def cleanup_path(path):
    """Cleanup a filesystem path -- remove ~s and extra slashes."""
    return os.path.abspath(os.path.normpath(os.path.expanduser(path)))

def fullpathlistdir(dirname):
    """Like os.listdir, but includes the full path to each file."""
    return [os.path.join(dirname, f) 
        for f in os.listdir(dirname)]

class LazyPipeline(pipes.Template):
    """A pipes.Template which can be pickle'd.  We return a special lazy file
    from open() so that the file object can be partially pickled."""
    def open(self, filename, rw):
        return LazyPipelineFile(self, filename, rw)

class LazyPipelineFile:
    """The result of LazyPipeline.open -- avoids opening the actual file
    as late as possible so that it can be pickle'd.  You probably don't
    want to create these on your own.  Also, note that, while it can be
    pickled, no state will be remembered."""
    def __init__(self, pipeline, filename, mode):
        self._pipeline = pipeline
        self._filename = filename
        self._mode = mode
        self._fileobj = None
    def __eq__(self, other):
        return hash(self) == hash(other)
    def __hash__(self):
        return hash(self._filename)
        # return hash((self._filename, tuple(self._pipeline.steps)))
    def __getinitargs__(self):
        """This lets us be pickled even after self._fileobj exists
        (which would prevent pickling).  It also means that _fileobj
        will change and not be remembered between picklings."""
        return (self._pipeline, self._filename, self._mode)
    def __getstate__(self):
        d = self.__dict__.copy()
        d['_fileobj'] = None # don't pickle the actual file object
        return d
    def __setstate__(self, state):
        self.__dict__.update(state)
    def __repr__(self):
        return "LazyPipelineFile%r" % (self.__getinitargs__(),)
    __str__ = __repr__
    def __getattr__(self, attr):
        if attr is 'filename':
            return self._filename

        # if we haven't opened the actual file yet, this is the time to do it
        if self.__dict__.get('_fileobj') is None:
            # can't call LazyPipeline.open, since that's what created us,
            # so we call the parent class's open method instead...clumsily
            parentopen = pipes.Template.open
            self._fileobj = parentopen(self._pipeline,
                self._filename, self._mode)

        return getattr(self._fileobj, attr)

def lockfile(fileobj, blocking=True, exclusive=True):
    """Frontend to fcntl.lockf.  If blocking is True, it will block
    until the lock is free.  Otherwise, it will raise an IOError."""
    import fcntl, time, random
    if exclusive:
        flags = fcntl.LOCK_EX
    else:
        flags = fcntl.LOCK_SH

    flags |= fcntl.LOCK_NB
    if blocking:
        while 1:
            try:
                fcntl.lockf(fileobj.fileno(), flags)
            except IOError, e:
                if e.strerror == "Resource temporarily unavailable":
                    # sleep somewhere between 0 and 2 seconds
                    time.sleep(random.random() * 2)
            else:
                break
    else:
        fcntl.lockf(fileobj.fileno(), flags)

def unlockfile(fileobj):
    """Unlock a file locked by lockfile (or really, fcntl.lockf)."""
    import fcntl
    fcntl.lockf(fileobj.fileno(), fcntl.LOCK_UN)

def islocked(fileobj):
    """Returns whether a file is locked using fcntl.lockf."""
    import fcntl

    flags = fcntl.LOCK_NB | fcntl.LOCK_EX
    try:
        fcntl.lockf(fileobj.fileno(), flags)
    except IOError, e:
        if e.strerror == "Resource temporarily unavailable":
            return True
    
    return False

def keepable_tempfile(mode='w+b', suffix='', prefix='tmp', dir=None, 
    keep=False):
    """If keep is True, acts like mkstemp, otherwise NamedTemporaryFile.
    In both cases, returns you a file object (unlike mkstemp)."""
    import tempfile
    if keep:
        import os
        fd, filename = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
        os.close(fd) # we'd open this with fdopen but for some reason, that
                     # hides the filename
        f = file(filename, mode)
        return f
    else:
        return tempfile.NamedTemporaryFile(mode=mode, suffix=suffix,
                                           prefix=prefix, dir=dir)

def split_input_into_sections(input_objects, outputdir, num_divisions=20, 
    verbose=True, filespec='division%s.gz', opener=GzipFile):
    """Split a file (or file-like object) into num_divisions
    roughly-equally sized sections.  If your input files include trees,
    make sure that they are all on one line (e.g. with ECParser.TreeReader)
    or they might be split across divisions."""
    import itertools
    num_lines = 0
    input_objects = [open_file_or_filename(obj) for obj in input_objects]
    temp_output = tempfile.NamedTemporaryFile(mode='r+w')
    for line in itertools.chain(input_objects):
        num_lines += 1
        temp_output.write(line.rstrip() + '\n')
    temp_output.seek(0)
    
    # the last section gets any extra lines
    section_size, extra_lines = divmod(num_lines, num_divisions)
    last_section_size = section_size + extra_lines
    
    if verbose:
        print "Making %d divisions of input data..." % num_divisions
        print num_divisions, num_lines
        print section_size, last_section_size
        print section_size * (num_divisions - 1)
        print (section_size * (num_divisions - 1)) + last_section_size
    
    # make a directory to put the division files
    mkdirparents(outputdir)
    
    # now we'll make a file for each division
    num_lines = 0
    current_division = -1 # this will get incremented soon
    current_division_file = None
    for line in temp_output:
        if (num_lines % section_size == 0) and \
           (current_division < (num_divisions - 1)):
            current_division += 1
            div_filename = os.path.join(outputdir,
                filespec % zfill_by_num(current_division, num_divisions))
            if current_division_file:
                current_division_file.flush()
            current_division_file = opener(div_filename, mode='w')
            if verbose:
                print "division", current_division, "at", num_lines, "lines"
        num_lines += 1
        current_division_file.write(line)
    current_division_file.flush()
        
    return section_size, last_section_size

