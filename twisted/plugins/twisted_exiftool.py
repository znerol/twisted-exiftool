from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os
from twisted.internet.endpoints import ProcessEndpoint
from twisted.internet.interfaces import IStreamClientEndpointStringParserWithReactor
from twisted.plugin import IPlugin
from twisted.python import procutils
from zope.interface import implementer


@implementer(IPlugin, IStreamClientEndpointStringParserWithReactor)
class ExiftoolProcessEndpoint(object):
    prefix = 'exiftool'
    _which = staticmethod(procutils.which)

    def _find_executable(self):
        binary_name = 'exiftool'
        executables = self._which(binary_name)
        if (len(executables)):
            executable = executables[0]
        else:
            # walk up the directory hierarchy and try to find the path to a
            # helper tool built with buildout.
            executable = os.path.abspath(__file__)
            while os.path.dirname(executable) != executable:
                candidate = os.path.join(executable, 'bin', 'exiftool', binary_name)
                if os.path.exists(candidate):
                    executable = candidate
                    break
                executable = os.path.dirname(executable)
            else:
                executable = None

        return executable

    def _parse(self, reactor, executable=None):
        if not executable:
            executable = self._find_executable()

        return ProcessEndpoint(reactor, executable, args=(executable, '-stay_open', 'True', '-@', '-'))

    def parseStreamClient(self, reactor, *args, **kwargs):
        return self._parse(reactor, *args, **kwargs)


processEndpoint = ExiftoolProcessEndpoint()
