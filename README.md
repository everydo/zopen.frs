================================================
FRS = File Repository System 文件库系统
================================================
frs.core is a pure python package for a simple file repository system(FRS). 
FRS use a virtual file system which map to the physical disk using a 
configuration file. FRS support trash box, metadata and attachments storge,
caching and more.

做什么
===============
1. 定义了一套虚拟的文件路径系统，可和实际的存储路径映射，避免直接和操作系统的文件系统打交道
#. 支持版本管理，可存储文件的历史版本。存放到(.frs目录中)
#. 支持缓存／数据转换，比如图片的各种大小的 格式转换和存储，word文件的html预览转换和存储
#. 支持垃圾箱，删除的文件可自动存放在垃圾箱里面
#. 三级目录映射

   - 网站 (zpath) -> FRS  (vpath)
   - FRS (vpath) -> ospath (path)

准备文件系统上的文件
=========================
找到临时文件夹: /tmp/frs

    >>> import os, tempfile, shutil
    >>> temp_dir = tempfile.gettempdir() + '/frs'
    >>> if os.path.exists(temp_dir):
    ...     shutil.rmtree(temp_dir)
    >>> os.mkdir(temp_dir)

创建缓存文件夹: /tmp/frscache

    >>> cache = temp_dir + '/frscache'
    >>> os.mkdir(cache)

创建文件夹结构::

 /tmp/frs/d1/f11
 /tmp/frs/lala/d2/d21
 /tmp/frs/lala/d2/f21

    >>> d1 = temp_dir + '/d1'
    >>> os.mkdir(d1)
    >>> f11 = d1 + '/f11'
    >>> open(f11, 'w').write('hello')
    >>> lala = temp_dir + '/lala'
    >>> os.mkdir(lala)
    >>> d2 = lala + '/d2'
    >>> os.mkdir(d2)
    >>> f21 = d2 + '/f21'
    >>> open(f21, 'w').write('hello')
    >>> d21 = d2 + '/d21'
    >>> os.mkdir(d21)


初始化
===================
得到一个:

    >>> frs_root = FRS()

什么都没有：

    >>> frs_root.listdir('/')
    []
 
Now we can mount some paths to the top folders:
 
    >>> frs_root.mount('d1', d1)
    >>> frs_root.mount('d2', d2)

同时设置缓存目录

    >>> frs_root.setCacheRoot(cache)

通过配置文件初始化
=========================
上面很麻烦，通过配置文件更简单

配置文件::

    >>> config = """
    ... [cache]
    ... path = /tmp/frscache
    ...
    ... [root]
    ... aa = /tmp/a
    ... bb = /tmp/b
    ...
    ... [site]
    ... / = /aa
    ... """

加载::

    >>> from zopen.frs import loadFRSFromConfig
    >>> frs_root = loadFRSFromConfig(config)

基本的文件系统功能
======================

    >>> sorted(frs_root.listdir('/'))
    ['d1', 'd2']
    >>> frs_root.isdir('/d1')
    True
    >>> frs_root.listdir('/d1')
    ['f11']
    >>> frs_root.isdir('/d1/f1')
    False
    >>> sorted(frs_root.listdir('/d2'))
    ['d21', 'f21']
    >>> frs_root.open('/d2/f21').read()
    'hello'

现在还不能跨区移动!

    >>> frs_root.move('/d2/f21', '/d1')
    Traceback (most recent call last):
        ...
    Exception: ...


自动映射
==================
其实配置文件中可以在site栏目中配置的。

也可以手工配置:

    >>> frs_root.mapSitepath2Vpath(u'/site1/members', u'/d2')
    >>> frs_root.mapSitepath2Vpath(u'/site2/members', u'/d2')
    >>> frs_root.mapSitepath2Vpath(u'/', u'/d1')

我们看看根据站点路径自动计算的路径:

    >>> frs_root.sitepath2Vpath('/58080_1/zopen/project/1222/files/uncategoried/aaa.doc')
    u'/d1/58080_1/zopen/project/1222/files/uncategoried/aaa.doc'

2个站点可以指向同一文件的:

    >>> frs_root.sitepath2Vpath('/site1/members/aaa.doc')
    u'/d2/aaa.doc'
    >>> frs_root.sitepath2Vpath('/site2/members/aaa.doc')
    u'/d2/aaa.doc'

