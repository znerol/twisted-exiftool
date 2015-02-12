from setuptools import setup

setup(
    name='TwistedExiftool',
    version='0.0.1',
    description='Exiftool protocol and stream endpoint plugin to be used with twisted',
    author='Lorenz Schori',
    author_email='lo@znerol.ch',
    packages=['twisted_exiftool'],
    package_data={
        'twisted.plugins': [
            'twisted/plugins/twisted_exiftool_process_endpoint.py',
        ]
    },
    install_requires=[
        'Twisted>=13.1',
        'zope.interface'
    ],
    zip_safe=False
)
