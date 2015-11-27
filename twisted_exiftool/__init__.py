from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import re
from twisted.internet import defer, error, protocol

try:
    from os import fsencode
except ImportError:
    from twisted_exiftool.compat import fsencode


class ExiftoolProtocol(protocol.Protocol):

    MAX_LENGTH = 2**16
    _buffer = None
    _pattern = re.compile(b'^{ready([0-9]+)}$', re.MULTILINE)
    _queue = None
    _stopped = None
    _tag = None

    def connectionMade(self):
        """
        Initializes the protocol.
        """
        self._buffer = b''
        self._queue = {}
        self._stopped = None
        self._tag = 0

    def dataReceived(self, data):
        """
        Parses chunks of bytes into responses.
        """
        l = len(self._buffer) + len(data)
        if (l > self.MAX_LENGTH):
            self.lengthLimitExceeded(l)
        self._buffer += data

        start = 0
        for match in self._pattern.finditer(self._buffer):
            # The start of the sentinel marks the end of the response.
            end = match.start()
            tag = int(match.group(1))
            self.responseReceived(self._buffer[start:end], tag)

            # Advance start position to the beginning of the next line
            start = match.end() + 1

        if start:
            self._buffer = self._buffer[start:]


    def responseReceived(self, data, tag):
        d = self._queue.pop(tag)
        d.callback(data)


    def lengthLimitExceeded(self, length):
        """
        Callback invoked when the incomming data would exceed the length limit
        appended to the buffer. The default implementation disconnects the
        transport.

        @param length: The total number of bytes
        @type length: C{int}
        """
        self.transport.loseConnection()


    def execute(self, *args):
        self._tag += 1

        args = tuple(args) + ('-execute{:d}'.format(self._tag), '')
        safe_args = [fsencode(arg) for arg in args]
        self.transport.write(b'\n'.join(safe_args))

        d = defer.Deferred()
        self._queue[self._tag] = d

        return d


    def loseConnection(self):
        if self._stopped:
            d = self._stopped
        elif self.connected:
            d = defer.Deferred()
            self._stopped = d
            self.transport.write(b'\n'.join((b'-stay_open', b'False', b'')))
        else:
            # Already disconnected.
            d = defer.success(self)

        return d


    def connectionLost(self, reason):
        self.connected = 0
        if self._stopped:
            self._stopped.callback(self if reason.check(error.ConnectionDone) else reason)
            self._stopped = None
        else:
            reason.raiseException()
