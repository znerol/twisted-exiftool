from twisted.internet import endpoints, reactor
from twisted.internet.endpoints import StandardErrorBehavior
from twisted.trial import unittest

class ClientStringTests(unittest.TestCase):
    """
    Tests for L{twisted.plugins.twisted_exiftool_process_endpoint.ExiftoolProcessEndpoint}.
    """

    def test_endpoint_with_executable_path(self):
        """
        When passed an exiftool strports description,
        L{endpoints.clientFromString} returns a L{ProcessEndpoint} instance
        initialized with the exiftool executable specified in the string.
        """
        ep = endpoints.clientFromString(reactor, b"exiftool:/some/path/to/exiftool")
        self.assertIsInstance(ep, endpoints.ProcessEndpoint)
        self.assertEqual(ep._executable, '/some/path/to/exiftool')
        self.assertEqual(ep._args, ('/some/path/to/exiftool', '-stay_open', 'True', '-@', '-'))
        self.assertEqual(ep._env, {})
        self.assertEqual(ep._path, None)
        self.assertEqual(ep._uid, None)
        self.assertEqual(ep._gid, None)
        self.assertEqual(ep._usePTY, 0)
        self.assertEqual(ep._childFDs, None)
        self.assertEqual(ep._errFlag, StandardErrorBehavior.LOG)
