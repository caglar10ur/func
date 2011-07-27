"""A very simple logger that tries to be concurrency-safe."""

import os, sys
import time
import traceback
import subprocess
import select

LOG_FILE    = '/var/log/nodemanager'

# basically define 3 levels
LOG_NONE=0
LOG_NODE=1
LOG_VERBOSE=2
# default is to log a reasonable amount of stuff for when running on operational nodes
LOG_LEVEL=1

def set_level(level):
    global LOG_LEVEL
    assert level in [LOG_NONE,LOG_NODE,LOG_VERBOSE]
    LOG_LEVEL=level

def verbose(msg):
    log('(v) '+msg,LOG_VERBOSE)

def log(msg,level=LOG_NODE):
    """Write <msg> to the log file if level >= current log level (default LOG_NODE)."""
    if (level > LOG_LEVEL):
        return
    try:
        fd = os.open(LOG_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0600)
        if not msg.endswith('\n'): msg += '\n'
        os.write(fd, '%s: %s' % (time.asctime(time.gmtime()), msg))
        os.close(fd)
    except OSError:
        sys.stderr.write(msg)
        sys.stderr.flush()

def log_exc(msg="",name=None):
    """Log the traceback resulting from an exception."""
    if name:
        log("%s: EXCEPTION caught <%s> \n %s" %(name, msg, traceback.format_exc()))
    else:
        log("EXCEPTION caught <%s> \n %s" %(msg, traceback.format_exc()))

#################### child processes
# avoid waiting until the process returns;
# that makes debugging of hanging children hard

class Buffer:
    def __init__ (self,message='log_call: '):
        self.buffer=''
        self.message=message

    def add (self,c):
        self.buffer += c
        if c=='\n': self.flush()

    def flush (self):
        if self.buffer:
            log (self.message + self.buffer)
            self.buffer=''

# time out in seconds - avoid hanging subprocesses - default is 5 minutes
default_timeout_minutes=5

# returns a bool that is True when everything goes fine and the retcod is 0
def log_call(command,timeout=default_timeout_minutes*60,poll=1):
    message=" ".join(command)
    log("log_call: running command %s" % message)
    verbose("log_call: timeout=%r s" % timeout)
    verbose("log_call: poll=%r s" % poll)
    trigger=time.time()+timeout
    result = False
    try:
        child = subprocess.Popen(command, bufsize=1,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        buffer = Buffer()
        while True:
            # see if anything can be read within the poll interval
            (r,w,x)=select.select([child.stdout],[],[],poll)
            if r: buffer.add(child.stdout.read(1))
            # is process over ?
            returncode=child.poll()
            # yes
            if returncode != None:
                buffer.flush()
                # child is done and return 0
                if returncode == 0:
                    log("log_call:end command (%s) completed" % message)
                    result=True
                    break
                # child has failed
                else:
                    log("log_call:end command (%s) returned with code %d" %(message,returncode))
                    break
            # no : still within timeout ?
            if time.time() >= trigger:
                buffer.flush()
                child.terminate()
                log("log_call:end terminating command (%s) - exceeded timeout %d s"%(message,timeout))
                break
    except: log_exc("failed to run command %s" % message)
    return result
