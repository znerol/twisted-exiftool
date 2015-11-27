from setuptools import setup

setup(
    name='TwistedExiftool',
    version='0.1.1',
    description='Exiftool protocol and stream endpoint plugin to be used with twisted',
    author='Lorenz Schori',
    author_email='lo@znerol.ch',
    url='https://github.com/znerol/twisted-exiftool',
    packages=['twisted_exiftool', 'twisted.plugins'],
    package_data={
        'twisted.plugins': [
            'twisted/plugins/twisted_exiftool.py',
        ]
    },
    install_requires=[
        'Twisted>=13.1',
        'zope.interface'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Graphics :: Capture'
    ],
)
