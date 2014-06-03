from setuptools import setup, find_packages

from guacg import VERSION

# @todo: install as server!


with open('README.md') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()


setup(
    name='gevent-guacamole',
    version=VERSION,
    url='https://github.com/mohabusama/gevent-guacamole',
    author='Mohab Usama',
    author_email='mohab.usama@gmail.com',
    description=('A gevent websocket Guacamole broker.'),
    long_description=README,
    license=LICENSE,
    zip_safe=False,
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
