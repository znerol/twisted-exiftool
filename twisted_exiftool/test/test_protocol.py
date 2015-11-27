"""
Tests for L{twisted_exiftool.ExiftoolProtocol}
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from twisted.internet import defer, error, protocol
from twisted.python import failure
from twisted.test import proto_helpers
from twisted.trial.unittest import TestCase
from twisted_exiftool import ExiftoolProtocol


class ExiftoolProtocolTest(TestCase):


    def setUp(self):
        factory = protocol.Factory.forProtocol(ExiftoolProtocol)
        self.proto = factory.buildProtocol(None)
        self.tr = proto_helpers.StringTransportWithDisconnection()
        self.tr.protocol = self.proto
        self.proto.makeConnection(self.tr)
        self.tag = 0


    def test_execute_one(self):
        self.tag += 1

        d = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), b'/path/to/file.jpg\n-execute%d\n' % (self.tag,))
        self.tr.clear()

        expected = "\n".join([
            b"ExifTool Version Number         : 9.74",
            b"File Name                       : file.jpg",
            b"Directory                       : /path/to",
            b""
        ])

        d.addCallback(self.assertEqual, expected)
        self.proto.dataReceived(b"%s{ready%d}\n" % (expected, self.tag))

        return d


    def test_execute_sequence(self):
        self.tag += 1
        d1 = self.proto.execute('/path/to/file.jpg')
        expected_command_1 = b'/path/to/file.jpg\n-execute%d\n' % self.tag
        expected_result_1 = b"\n".join([
            b"ExifTool Version Number         : 9.74",
            b"File Name                       : file.jpg",
            b"Directory                       : /path/to",
            b""
        ])
        d1.addCallback(self.assertEqual, expected_result_1)

        self.tag += 1
        d2 = self.proto.execute('-v', '-u', '/path/to/other.png')
        expected_command_2 = b'-v\n-u\n/path/to/other.png\n-execute%d\n' % self.tag
        expected_result_2 = b"\n".join([
            "PNG IHDR (13 bytes):",
            "  + [BinaryData directory, 13 bytes]",
            "  | ImageWidth = 640",
            "  | ImageHeight = 480",
            "  | BitDepth = 8",
            "  | ColorType = 2",
            "  | Compression = 0",
            "  | Filter = 0",
            "  | Interlace = 0",
            ""
        ])
        d2.addCallback(self.assertEqual, expected_result_2)

        self.assertEqual(self.tr.value(), expected_command_1 + expected_command_2)
        self.tr.clear()

        self.proto.dataReceived(b"%s{ready%d}\n" % (expected_result_1, self.tag - 1))
        self.proto.dataReceived(b"%s{ready%d}\n" % (expected_result_2, self.tag))

        return defer.DeferredList([d1, d2])


    def test_empty_response(self):
        self.tag += 1

        d = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), b'/path/to/file.jpg\n-execute%d\n' % (self.tag,))
        self.tr.clear()

        d.addCallback(self.assertEqual, b'')
        self.proto.dataReceived(b"{ready%d}\n" % self.tag)

        return d


    def test_chunked_response(self):
        self.tag += 1

        d = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), b'/path/to/file.jpg\n-execute%d\n' % (self.tag,))
        self.tr.clear()

        expected = "\n".join([
            b"ExifTool Version Number         : 9.74",
            b"File Name                       : file.jpg",
            b"Directory                       : /path/to",
            b""
        ])

        d.addCallback(self.assertEqual, expected)

        response = b"%s{ready%d}\n" % (expected, self.tag)
        s = 16
        for i in xrange(0, len(response), s):
            self.proto.dataReceived(response[i:i+s])

        return d

    def test_disconnect(self):
        self.assertEqual(self.proto.connected, True)

        # Call loseConnection on protocol
        d = self.proto.loseConnection()

        self.assertEqual(self.tr.value(), b'-stay_open\nFalse\n')

        # Simulate graceful termination of process.
        self.proto.connectionLost(failure.Failure(error.ConnectionDone()))
        self.assertEqual(self.proto.connected, False)
        self.tr.clear()

        d.addCallback(self.assertEqual, self.proto)

        return d

    def test_connection_lost(self):
        self.assertEqual(self.proto.connected, True)

        self.failUnlessRaises(error.ConnectionLost, self.proto.connectionLost, failure.Failure(error.ConnectionLost('process exited')))

        self.assertEqual(self.tr.value(), b'')
        self.assertEqual(self.proto.connected, False)
        self.tr.clear()
