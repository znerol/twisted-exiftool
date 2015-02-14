"""
Tests for L{twisted_exiftool.ExiftoolProtocol}
"""

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
        self.assertEqual(self.tr.value(), '/path/to/file.jpg\n-execute%d\n' % (self.tag,))
        self.tr.clear()

        expected = "\n".join([
            "ExifTool Version Number         : 9.74",
            "File Name                       : file.jpg",
            "Directory                       : /path/to",
            ""
        ])

        d.addCallback(self.assertEqual, expected)
        self.proto.dataReceived("%s{ready%d}\n" % (expected, self.tag))

        return d


    def test_execute_sequence(self):
        self.tag += 1
        d1 = self.proto.execute('/path/to/file.jpg')
        expected_command_1 = '/path/to/file.jpg\n-execute%d\n' % self.tag
        expected_result_1 = "\n".join([
            "ExifTool Version Number         : 9.74",
            "File Name                       : file.jpg",
            "Directory                       : /path/to",
            ""
        ])
        d1.addCallback(self.assertEqual, expected_result_1)

        self.tag += 1
        d2 = self.proto.execute('-v', '-u', '/path/to/other.png')
        expected_command_2 = '-v\n-u\n/path/to/other.png\n-execute%d\n' % self.tag
        expected_result_2 = "\n".join([
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

        self.proto.dataReceived("%s{ready%d}\n" % (expected_result_1, self.tag - 1))
        self.proto.dataReceived("%s{ready%d}\n" % (expected_result_2, self.tag))

        return defer.DeferredList([d1, d2])


    def test_empty_response(self):
        self.tag += 1

        d = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), '/path/to/file.jpg\n-execute%d\n' % (self.tag,))
        self.tr.clear()

        d.addCallback(self.assertEqual, '')
        self.proto.dataReceived("{ready%d}\n" % self.tag)

        return d


    def test_chunked_response(self):
        self.tag += 1

        d = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), '/path/to/file.jpg\n-execute%d\n' % (self.tag,))
        self.tr.clear()

        expected = "\n".join([
            "ExifTool Version Number         : 9.74",
            "File Name                       : file.jpg",
            "Directory                       : /path/to",
            ""
        ])

        d.addCallback(self.assertEqual, expected)

        response = "%s{ready%d}\n" % (expected, self.tag)
        s = 16
        for i in xrange(0, len(response), s):
            self.proto.dataReceived(response[i:i+s])

        return d

    def test_disconnect(self):
        self.assertEqual(self.proto.connected, True)

        # Call loseConnection on protocol
        d = self.proto.loseConnection()

        self.assertEqual(self.tr.value(), '-stay_open\nFalse\n')
        self.assertEqual(self.proto.connected, False)
        self.tr.clear()

        d.addCallback(self.assertEqual, self.proto)

        return d

    def test_connection_lost(self):
        self.assertEqual(self.proto.connected, True)

        self.failUnlessRaises(error.ConnectionLost, self.proto.connectionLost, failure.Failure(error.ConnectionLost('process exited')))

        self.assertEqual(self.tr.value(), '')
        self.assertEqual(self.proto.connected, False)
        self.tr.clear()
