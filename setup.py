from setuptools import setup

setup(
    name='TwistedExiftool',
    version='0.1.0',
    description='Exiftool protocol and stream endpoint plugin to be used with twisted',
    author='Lorenz Schori',
    author_email='lo@znerol.ch',
    packages=['twisted_exiftool'],
    package_data={
        'twisted.plugins': [
            'twisted/plugins/twisted_exiftool.py',
        ]
    },
    install_requires=[
        'Twisted>=13.1',
        'zope.interface'
    ],
    zip_safe=False
)
