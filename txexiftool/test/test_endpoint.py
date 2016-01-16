from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from twisted.internet import endpoints, reactor
from twisted.internet.endpoints import StandardErrorBehavior
from twisted.trial import unittest

class ClientStringTests(unittest.TestCase):
    """
    Tests for L{twisted.plugins.txexiftool.ExiftoolProcessEndpoint}.
    """

    def setUp(self):
        from twisted.plugins.txexiftool import ExiftoolProcessEndpoint
        ExiftoolProcessEndpoint._which = self.which_stub


    def test_endpoint_with_system_provided_executable(self):
        """
        When passed a strports description, L{endpoints.clientFromString}
        returns a L{ProcessEndpoint} instance initialized with the exiftool
        executable installed in the system.
        """
        ep = endpoints.clientFromString(reactor, u'exiftool')
        self.assertIsInstance(ep, endpoints.ProcessEndpoint)
        self.assertEqual(ep._executable, '/system/path/to/exiftool')
        self.assertEqual(ep._args, ('/system/path/to/exiftool', '-stay_open', 'True', '-@', '-'))
        self.assertEqual(ep._env, {})
        self.assertEqual(ep._path, None)
        self.assertEqual(ep._uid, None)
        self.assertEqual(ep._gid, None)
        self.assertEqual(ep._usePTY, 0)
        self.assertEqual(ep._childFDs, None)
        self.assertEqual(ep._errFlag, StandardErrorBehavior.LOG)


    def test_endpoint_with_executable_path(self):
        """
        When passed a strports description containing the path to the exiftool
        executable, L{endpoints.clientFromString} returns a L{ProcessEndpoint}
        instance initialized with the specified executable.
        """
        ep = endpoints.clientFromString(reactor, u'exiftool:/some/path/to/exiftool')
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


    def which_stub(self, name):
        return ['/system/path/to/exiftool']
