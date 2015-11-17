import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()

setup (
    name='zopen.frs',
    version='1.2.2',
    author='panjy',
    author_email='panjunyong@gmail.com',
    description='zopen frs management',
    long_description=README,
    license='Private',
    keywords='zope3 z3c rpc server client operation',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
    ],
    url='http://pypi.zopen.cn/zopen.frs',
    packages=find_packages(),
    include_package_data=True,
    namespace_packages=['zopen'],
    install_requires=[
        'setuptools',
        # tests only
        'zope.datetime',
    ],
    zip_safe=False,
)
