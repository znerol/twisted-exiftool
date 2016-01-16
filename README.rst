txExiftool
==========

.. image:: https://travis-ci.org/znerol/txexiftool.svg?branch=master
    :target: https://travis-ci.org/znerol/txexiftool


Exiftool_ protocol and stream endpoint plugin to be used with twisted_.

.. _Exiftool: http://www.sno.phy.queensu.ca/~phil/exiftool/
.. _twisted: https://twistedmatrix.com/


Usage
-----

::

    from twisted.internet import defer, endpoints, protocol, reactor
    from txexiftool import ExiftoolProtocol

    @defer.inlineCallbacks
    def test():
        # Construct an exiftool endpoint. If the tool is installed in a custom
        # location, specify the path to the binary as the first argument. E.g.
        # 'exiftool:/path/to/exiftool'
        ep = endpoints.clientFromString(reactor, 'exiftool')

        # Instantiate the protocol by connecting to the endpoint
        f = protocol.Factory.forProtocol(ExiftoolProtocol)
        p = yield ep.connect(f)

        # Run commands and retrieve results.
        metadata = yield p.execute('-j', '/usr/share/pixmaps/gtkvim.png')
        print metadata

        # Disconnect
        yield p.loseConnection()

        reactor.stop()

    reactor.callWhenRunning(test)
    reactor.run()


License
-------

The software is subject to the MIT license.
