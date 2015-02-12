import codecs
import sys
from twisted.internet import defer, error
from twisted.protocols import basic
from twisted.python import log

# This code has been adapted from Lib/os.py in the Python source tree (sha1
# 265e36e277f3). The fragment was copied from pyexiftool by Sven Marnach
# released under the GPL and the revised BSD lisence.
# https://github.com/smarnach/pyexiftool
def _fscodec():
    encoding = sys.getfilesystemencoding()
    errors = "strict"
    if encoding != "mbcs":
        try:
            codecs.lookup_error("surrogateescape")
        except LookupError:
            pass
        else:
            errors = "surrogateescape"

    def fsencode(filename):
        """
        Encode filename to the filesystem encoding with 'surrogateescape' error
        handler, return bytes unchanged. On Windows, use 'strict' error handler if
        the file system encoding is 'mbcs' (which is the default encoding).
        """
        if isinstance(filename, bytes):
            return filename
        else:
            return filename.encode(encoding, errors)

    return fsencode

fsencode = _fscodec()
del _fscodec

class ExiftoolProtocol(basic.LineOnlyReceiver):

    delimiter = b'\n'
    MAX_LENGTH = 65536

    def __init__(self, default_args = ()):
        self.default_args = tuple(default_args)
        self._lines = []
        self._queue = {}
        self._stopped = None
        self._tag = 0


    def connectionMade(self):
        # Work around http://twistedmatrix.com/trac/ticket/6606
        try:
            test = self.transport.disconnecting
        except AttributeError:
            self.transport.disconnecting = False


    def lineReceived(self, line):
        if (line.startswith('{ready')):
            tag = int(line[6:-1])
            self.responseReceived(self.delimiter.join(self._lines), tag)
            self._lines = []
        else:
            self._lines.append(line)


    def responseReceived(self, data, tag):
        d = self._queue.pop(tag)
        d.callback(data)


    def execute(self, *args):
        self._tag += 1

        safe_args = map(fsencode, self.default_args + tuple(args) + ('-execute' + str(self._tag), ''))
        self.transport.write("\n".join(safe_args))

        d = defer.Deferred()
        self._queue[self._tag] = d

        return d


    def loseConnection(self):
        if self.connected and not self._stopped:
            self._stopped = defer.Deferred()
            self.transport.write("\n".join(('-stay_open', 'False', '')))
            self.transport.loseConnection()

        return self._stopped


    def connectionLost(self, reason):
        self.connected = 0
        if self._stopped:
            self._stopped.callback(self if reason.check(error.ConnectionDone) else reason)
            self._stopped = None
        else:
            log.err(reason)
