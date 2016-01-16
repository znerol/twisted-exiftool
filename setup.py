from setuptools import setup

setup(
    name='txExiftool',
    version='0.1.3',
    description='Exiftool protocol and stream endpoint plugin to be used with Twisted',
    author='Lorenz Schori',
    author_email='lo@znerol.ch',
    url='https://github.com/znerol/txexiftool',
    packages=['txexiftool', 'twisted.plugins'],
    package_data={
        'twisted.plugins': [
            'twisted/plugins/txexiftool.py',
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
