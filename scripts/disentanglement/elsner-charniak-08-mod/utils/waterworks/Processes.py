import select, os, sys
from popen2 import Popen3

def bettersystem(command, stdout=None, stderr=None):
    """Select-based version of commands.getstatusoutput.  stdout and stderr
    are stream or stream-like objects.  Returns the exit status."""
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    p = Popen3(command, capturestderr=True)
    p_out, p_err = p.fromchild, p.childerr
    fd_out = p_out.fileno()
    fd_err = p_err.fileno()

    out_finished = False
    err_finished = False
    while 1:
        rlist, _, _ = select.select([p_out, p_err], [], [])
        if not rlist:
            break

        if p_out in rlist:
            output = os.read(fd_out, 1024)
            if output == '':
                out_finished = True
            else:
                stdout.write(output)
                stdout.flush()
        if p_err in rlist:
            output = os.read(fd_err, 1024)
            if output == '':
                err_finished = True
            else:
                stderr.write(output)
                stderr.flush()

        if out_finished and err_finished and p.poll() != -1:
            break

    return p.wait()

# TODO this might not belong here
def selectbasedreader(pollobjs, read_amount=1024, timeout=0.1):
    result = ''
    while 1:
        rlist, _, _ = select.select(pollobjs, [], [], timeout)
        if not rlist:
            continue

        if rlist:
            f = rlist[0]
            # print 'f', f, dir(f)
            output = os.read(f.fileno(), read_amount)
            if not output:
                return
            yield f, output

class Pipe:
    """Captures some common behaviors about running data through a pipe."""
    def __init__(self, command):
        self.pipe = Popen3(command, capturestderr=True)
        self.command = command
    def feed(self, data):
        self.pipe.tochild.write(data)
        self.pipe.tochild.flush()
    def close(self):
        self.pipe.tochild.close()
    def check(self, read_amount=1024, timeout=0, on_not_ready_func=None,
              return_on_finished=True):
        # print "check()", self.command
        p_out, p_err = self.pipe.fromchild, self.pipe.childerr
        fd_out = p_out.fileno()
        fd_err = p_err.fileno()
        result = ''
        while 1:
            rlist, _, _ = select.select([p_out], [], [], timeout)
            # print 'rlist', rlist
            if not rlist:
                if on_not_ready_func is None:
                    # print 'spit ""'
                    yield ''
                else:
                    # print 'func', on_not_ready_func
                    on_not_ready_func()

            if p_out in rlist:
                output = os.read(fd_out, read_amount)
                # print 'yield', repr(output)
                yield output

            # print 'poll', self.pipe.poll()
            if return_on_finished and self.pipe.poll() != -1:
                # print 'poll', self.pipe.poll()
                return
    def process(self, data, timeout=1, verifier=None):
        """Rechecks with a timeout until there is no more data coming
        from the pipe.  If there are more elaborate cues about when to
        stop reading, you may need to use check() directly.  verifier()
        is a predicate applied to the output.  If it raises an exception,
        we will wait for more data."""
        from cStringIO import StringIO
        self.feed(data)
        result = ''
        while 1:
            for newdata in self.check(timeout=timeout):
                if result.strip() and newdata == '':
                    break
                result += newdata

            if verifier:
                try:
                    verifier(result)
                    break
                except:
                    pass # loop again, look for more data
            else:
                break
        return result

if __name__ == "__main__":
    p = Pipe("rev")
    p.feed('splarg')
    p.close()

    import time
    for x in p.check(on_not_ready_func=lambda: time.sleep(0.1),
                     return_on_finished=False):
        print repr(x)
        if x:
            break
