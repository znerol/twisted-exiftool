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
        self.assertEqual(self.tr.value(), '/path/to/file.jpg\n-execute{:d}\n'.format(self.tag).encode('utf-8'))
        self.tr.clear()

        expected = '\n'.join([
            'ExifTool Version Number         : 9.74',
            'File Name                       : file.jpg',
            'Directory                       : /path/to',
            ''
        ])

        d.addCallback(self.assertEqual, expected.encode('utf-8'))
        self.proto.dataReceived('{:s}{{ready{:d}}}\n'.format(expected, self.tag).encode('utf-8'))

        return d


    def test_execute_sequence(self):
        self.tag += 1
        d1 = self.proto.execute('/path/to/file.jpg')
        expected_command_1 = '/path/to/file.jpg\n-execute{:d}\n'.format(self.tag).encode('utf-8')
        expected_result_1 = '\n'.join([
            'ExifTool Version Number         : 9.74',
            'File Name                       : file.jpg',
            'Directory                       : /path/to',
            ''
        ])
        d1.addCallback(self.assertEqual, expected_result_1.encode('utf-8'))

        self.tag += 1
        d2 = self.proto.execute('-v', '-u', '/path/to/other.png')
        expected_command_2 = '-v\n-u\n/path/to/other.png\n-execute{:d}\n'.format(self.tag).encode('utf-8')
        expected_result_2 = '\n'.join([
            'PNG IHDR (13 bytes):',
            '  + [BinaryData directory, 13 bytes]',
            '  | ImageWidth = 640',
            '  | ImageHeight = 480',
            '  | BitDepth = 8',
            '  | ColorType = 2',
            '  | Compression = 0',
            '  | Filter = 0',
            '  | Interlace = 0',
            ''
        ])
        d2.addCallback(self.assertEqual, expected_result_2.encode('utf-8'))

        self.assertEqual(self.tr.value(), expected_command_1 + expected_command_2)
        self.tr.clear()

        self.proto.dataReceived('{:s}{{ready{:d}}}\n'.format(expected_result_1, self.tag - 1).encode('utf-8'))
        self.proto.dataReceived('{:s}{{ready{:d}}}\n'.format(expected_result_2, self.tag).encode('utf-8'))

        return defer.DeferredList([d1, d2])


    def test_empty_response(self):
        self.tag += 1

        d = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), '/path/to/file.jpg\n-execute{:d}\n'.format(self.tag).encode('utf-8'))
        self.tr.clear()

        d.addCallback(self.assertEqual, b'')
        self.proto.dataReceived('{{ready{:d}}}\n'.format(self.tag).encode('utf-8'))

        return d


    def test_chunked_response(self):
        self.tag += 1

        d = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), '/path/to/file.jpg\n-execute{:d}\n'.format(self.tag).encode('utf-8'))
        self.tr.clear()

        expected = '\n'.join([
            'ExifTool Version Number         : 9.74',
            'File Name                       : file.jpg',
            'Directory                       : /path/to',
            ''
        ])

        d.addCallback(self.assertEqual, expected.encode('utf-8'))

        response = '{:s}{{ready{:d}}}\n'.format(expected, self.tag)
        s = 16
        for i in range(0, len(response), s):
            self.proto.dataReceived(response[i:i+s].encode('utf-8'))

        return d

    @defer.inlineCallbacks
    def test_disconnect(self):
        self.assertEqual(self.proto.connected, True)

        # Call loseConnection on protocol
        d = self.proto.loseConnection()

        self.assertEqual(self.tr.value(), b'-stay_open\nFalse\n')

        # Simulate graceful termination of process.
        self.proto.connectionLost(failure.Failure(error.ConnectionDone()))
        self.assertEqual(self.proto.connected, False)
        self.tr.clear()

        result = yield d
        self.assertEqual(result, self.proto)

        # Try to execute a job on the closed protocol.
        job = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), b'')
        self.tr.clear()

        yield self.assertFailure(job, error.ConnectionClosed)

    @defer.inlineCallbacks
    def test_connection_lost(self):
        self.tag += 1

        pending_job = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), '/path/to/file.jpg\n-execute{:d}\n'.format(self.tag).encode('utf-8'))
        self.tr.clear()

        self.assertEqual(self.proto.connected, True)

        self.failUnlessRaises(error.ConnectionLost, self.proto.connectionLost, failure.Failure(error.ConnectionLost('process exited')))

        self.assertEqual(self.tr.value(), b'')
        self.assertEqual(self.proto.connected, False)
        self.tr.clear()

        # Ensure that the errback is triggered on a pending job when the
        # connection to exiftool was lost.
        yield self.assertFailure(pending_job, error.ConnectionLost)

        # Try to execute a job on the closed protocol.
        job = self.proto.execute('/path/to/file.jpg')
        self.assertEqual(self.tr.value(), b'')
        self.tr.clear()

        yield self.assertFailure(job, error.ConnectionClosed)
