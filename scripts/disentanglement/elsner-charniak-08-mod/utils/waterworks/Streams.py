import sys
from cStringIO import StringIO

class stream_prefixer:
   def __init__(self, prefix, originalstream):
       self.prefix = prefix
       self.originalstream = originalstream

       self._should_print_prefix = True
   def write(self, text):
       if self._should_print_prefix:
           text = self.prefix + text
           self._should_print_prefix = False
       if text.endswith('\n'):
           self._should_print_prefix = True
       # not super elegant -- don't prefix last newline yet
       text = text[:-1].replace('\n', '\n' + self.prefix) + text[-1]
       self.originalstream.write(text)
   def __getattr__(self, attr):
       return getattr(self.originalstream, attr)

def prefix_stdout(prefix):
    sys.stdout = stream_prefixer(prefix, sys.stdout)

class Tee:
    def __init__(self, stream):
        self.stream = stream
        self.output = StringIO()
    def write(self, s):
        self.stream.write(s)
        self.seek(0, 2)
        self.output.write(s)
    def __str__(self):
        self.seek(0, 0)
        return self.output.read()
    def __getattr__(self, attr):
        return getattr(self.output, attr)

def tee_stdout():
    return Tee(sys.stdout)
def tee_stderr():
    return Tee(sys.stderr)

if __name__ == "__main__":
    sys.stdout = tee_stdout()

    print "hi!"
    print 'str()ed:', repr(str(sys.stdout))
