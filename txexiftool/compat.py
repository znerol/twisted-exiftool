"""
Backport of Python 3.2 fsencode function

This code has been adapted from Lib/os.py in the Python source tree (sha1
265e36e277f3). The fragment was copied from pyexiftool by Sven Marnach released
under the GPL and the revised BSD lisence.
https://github.com/smarnach/pyexiftool
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import codecs
import sys

def _fscodec():
    encoding = sys.getfilesystemencoding()
    errors = 'strict'
    if encoding != 'mbcs':
        try:
            codecs.lookup_error('surrogateescape')
        except LookupError:
            pass
        else:
            errors = 'surrogateescape'

    def fsencode(filename):
        """
        Encode filename to the filesystem encoding with 'surrogateescape' error
        handler, return bytes unchanged. On Windows, use 'strict' error handler
        if the file system encoding is 'mbcs' (which is the default encoding).
        """
        if isinstance(filename, bytes):
            return filename
        else:
            return filename.encode(encoding, errors)

    return fsencode

fsencode = _fscodec()
del _fscodec
