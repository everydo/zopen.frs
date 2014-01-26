################################
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

setup (
    name='zopen.frs',
    version='1.0',
    author = "panjy",
    author_email = "panjunyong@gmail.com",
    description = "zopen frs management",
    license = "Private",
    keywords = "zope3 z3c rpc server client operation",
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        ],
    url = 'http://pypi.zopen.cn/zopen.frs',
    packages = find_packages(),
    include_package_data = True,
    namespace_packages= ['zopen', ],
    install_requires = [
         'setuptools',
         # tests only
        'zope.datetime',
        ],
    zip_safe = False,
    entry_points = """
    """
)
