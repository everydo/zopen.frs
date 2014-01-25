################################
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

setup (
    name='zopen.frs.core',
    version='0.1.1dev',
    author = "panjy",
    author_email = "panjunyong@gmail.com",
    description = "zopen frs management",
    license = "Private",
    keywords = "zope3 z3c rpc server client operation",
    classifiers = [
        'Development Status :: 4 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: Chinese',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url = 'http://pypi.zopen.cn/zopen.frs.core',
    packages = find_packages(),
    include_package_data = True,
    namespace_packages= ['zopen', 'zopen.frs'],
    install_requires = [
         'setuptools',
         'Gnosis_Utils',
         # tests only
        'zope.datetime',
        ],
    zip_safe = False,
    entry_points = """
    """
)
