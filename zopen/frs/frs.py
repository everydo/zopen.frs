# -*- encoding:utf-8 -*-

import os
import shutil
import fnmatch
import posixpath
from configparser import ConfigParser

from .utils import ucopytree, umove
from .archive import ArchiveSupportMixin
from .recycle import RecycleMixin
from .cache import CacheMixin
from .config import FRS_ARCHIVED_FOLDER_NAME


def loadFRSFromConfig(buf):
    parser = ConfigParser()
    parser.read_string(buf)

    frs = FRS()
    cache_path = parser.get('cache', 'path')
    frs.setCacheRoot(cache_path)

    roots = parser.items('root')
    for name, path in roots:
        path = os.path.normpath(path)
        frs.mount(name, path)

    roots = parser.items('site')
    for site_path, vpath in roots:
        frs.mapSitepath2Vpath(site_path, vpath)
    return frs


class FRS(ArchiveSupportMixin, RecycleMixin, CacheMixin):
    '''
    vfs = virtual file system
    a virtual posix like file system

    site path -> virtual path -> os path
    site_vpath_mount  &  vpath_os_mount:
    '''
    def __init__(self, cache_root='/tmp', dotfrs='.frs', version='json'):
        self._site_vfs_map = []
        self._vfs_os_map = dict()
        self.dotfrs = dotfrs
        self.cache_root = cache_root
        self.version = version

    def mount(self, name, path):
        '''
        mount filesystem path to vfs
        only support mount top dirs
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        if name.startswith('/'):
            name = name[1:]
        self._vfs_os_map[name] = path

    def mapSitepath2Vpath(self, site_path, vpath):
        ''' map vpath to site path '''
        self._site_vfs_map.append((site_path, vpath))

    def setCacheRoot(self, path):
        ''' where to push caches '''
        self.cache_root = path
        self.mount('cache', path)

    def sitepath2Vpath(self, site_path):
        if site_path[-1] != '/':
            site_path += '/'

        # 历史版本，直接找到对应的历史版本文件夹
        # /site/path/++versions++/version
        if '/++versions++/' in site_path:
            site_path, version = site_path.split('/++versions++/')
            site_path = site_path.split('/')
            site_path.append(self.dotfrs)
            site_path.append(FRS_ARCHIVED_FOLDER_NAME)
            site_path.append(version)
            site_path = '/'.join(site_path)

        for _spath, _vpath in self._site_vfs_map:
            if _spath[-1] != '/':
                _spath += '/'

            if site_path.startswith(_spath):
                if _vpath[-1] != '/':
                    _vpath += '/'

                result = _vpath + site_path[len(_spath):]
                if result[-1] == '/':
                    return result[:-1]
                return result
        raise ValueError('can not find a frs path for site path %s' % site_path)

    def vpath(self, ospath):
        ''' transform ospath to vpath '''
        for root, path in self._vfs_os_map.items():
            if ospath.startswith(path + '/'):
                return '/%s%s' % (root, ospath[len(path):])

    def ospath(self, vpath):
        ''' transform to a real os path '''
        if not vpath.startswith('/'):
            raise OSError(vpath)
        parts = vpath.split('/')
        try:
            toppath = self._vfs_os_map[parts[1]]
        except KeyError:
            if parts[1] == self.dotfrs:
                try:
                    toppath = self._vfs_os_map[parts[2]]
                except:
                    raise OSError(vpath)
                basename = os.path.basename(toppath)
                basedir = os.path.dirname(toppath)
                return os.path.join(basedir, self.dotfrs, basename, *parts[3:])
            raise OSError(vpath)
        return os.path.join(toppath, *parts[2:])

    def frspath(self, vpath, *frs_subpaths):
        '''
        It is another kind of joinpath, which returns path in the .frs folder.
        '''
        return self.joinpath(self.dirname(vpath),
                             self.dotfrs,
                             self.basename(vpath),
                             *frs_subpaths)

    def exists(self, vpath):
        try:
            path = self.ospath(vpath)
        except OSError:
            return False
        return os.path.exists(path)

    def joinpath(self, *arg):
        return posixpath.join(*arg)

    def basename(self, path):
        return posixpath.basename(path)

    def splitext(self, name):
        return os.path.splitext(name)

    def stat(self, vpath):
        return os.stat(self.ospath(vpath))

    def dirname(self, path):
        return posixpath.dirname(path)

    def ismount(self, vpath):
        '''
        return if vpath is a mount folder
        '''
        return vpath[1:] in self.listdir('/')

    def isdir(self, vpath):
        return os.path.isdir(self.ospath(vpath))

    def isfile(self, vpath):
        return os.path.isfile(self.ospath(vpath))

    def atime(self, vpath):
        return os.path.getatime(self.ospath(vpath))

    def mtime(self, vpath):
        return os.path.getmtime(self.ospath(vpath))

    def ctime(self, vpath):
        return os.path.getctime(self.ospath(vpath) )

    def getsize(self, vpath):
        return os.path.getsize(self.ospath(vpath) )

    def listdir(self, vpath, pattern=None):
        if vpath == '/':
             return self._vfs_os_map.keys()
        names = os.listdir(self.ospath(vpath))
        if pattern is not None:
            names = fnmatch.filter(names, pattern)

        names = [name for name in names if not name.startswith(self.dotfrs)]
        return names

    def dirs(self, vpath, pattern=None):
        names = [name for name in self.listdir(vpath, pattern)
	                if self.isdir(self.joinpath(vpath, name))]
        return names

    def files(self, vpath, pattern=None):
        names = [name for name in self.listdir(vpath, pattern)
	                if self.isfile(self.joinpath(vpath, name))]
        return names

    def open(self, vpath, mode='r'):
        return open(self.ospath(vpath), mode)

    def move(self, vpath1, vpath2):
        # can't remove mount folder
        if self.ismount(vpath1):
            raise Exception("can't remove mount folder %s" % vpath1)
        if self.ismount(vpath2):
            raise Exception("can't move to mount folder %s" % vpath2)

        umove(self.ospath(vpath1), self.ospath(vpath2))

    def mkdir(self, vpath, mode=0o777):
        os.mkdir(self.ospath(vpath), mode)

    def makedirs(self, vpath, mode=0o777):
        os.makedirs(self.ospath(vpath), mode)

    def getNewName(self, path, name):
        while self.exists(self.joinpath(path, name)):
            name = 'copy_of_' + name
        return name

    def remove(self, vpath):
        ''' remove a file path'''
        os.remove(self.ospath(vpath) )

    def copyfile(self, vSrc, vDst):
        shutil.copyfile(self.ospath(vSrc), self.ospath(vDst))

    def copytree(self, vSrc, vDst):
        # copy2 don't work well with encoding
        # in fact it is os.utime don't work well
        ossrc = self.ospath(vSrc)
        osdst = self.ospath(vDst)
        ucopytree(ossrc, osdst, symlinks=False)

    def rmtree(self, vpath, ignore_errors=False, onerror=None):
        # can't remove mount folder
        if self.ismount(vpath):
            raise Exception("can't remove mount folder %s" % vpath)

        shutil.rmtree(self.ospath(vpath), ignore_errors, onerror)

    def touch(self, vpath):
        fd = os.open(self.ospath(vpath), os.O_WRONLY | os.O_CREAT, 0o666)
        os.close(fd)

    def walk(self, top, topdown=True, onerror=None):
        if top == '/':
            mount_dirs = self._vfs_os_map.keys()
            yield '/', mount_dirs,[]
            for name in mount_dirs:
                for item in self.walk('/' + name, topdown, onerror):
                    yield item
        else:
            top_ospath = os.path.normpath(self.ospath(top))
            top_ospath_len = len(top_ospath)
            for dirpath, dirnames, filenames in os.walk(top_ospath,topdown,onerror):

                if self.dotfrs in dirnames:
                    dirnames.remove(self.dotfrs)

                if dirnames or filenames:
                    dir_sub_path = dirpath[top_ospath_len+1:].replace(os.path.sep,  '/')
                    if dir_sub_path:
                        yield self.joinpath(top, dirpath[top_ospath_len+1:].replace(os.path.sep,  '/')), dirnames, filenames
                    else:
                        yield top, dirnames, filenames

    # asset management

    def removeAsset(self, path):
        frsPath = self.frspath(path)
        if self.exists(frsPath):
            self.rmtree(frsPath)

        if self.exists(path):
            if self.isfile(path):
                self.remove(path)
            else:
                self.rmtree(path)

        CacheMixin.removeCache(self, path)

    def moveAsset(self, src, dst):
        '''
        rename or move a file or folder
        '''
        frsSrc = self.frspath(src)
        if self.exists(frsSrc):
            frsDst = self.frspath(dst)
            if not self.exists( self.dirname(frsDst) ):
                self.makedirs(self.dirname(frsDst))
            self.move(frsSrc, frsDst )

        if not self.exists( self.dirname(dst) ):
            self.makedirs( self.dirname(dst) )
        self.move(src, dst)

        CacheMixin.moveCache(self, src, dst)

    def copyAsset(self, src, dst, **kw):
        '''
        copy folder / file and associated subfiles, not include archives
        don't keep stat
        '''
        if not self.exists(src):
            raise ValueError("source path is not exists: %s" % src)

        if self.isfile(src):
            self.copyfile(src, dst)
        else:
            # copy folder
            if not self.exists(dst):
                self.makedirs(dst)
            for name in self.listdir(src):
                self.copyAsset(self.joinpath(src, name), self.joinpath(dst, name), copycache=0)

        # copy cache
        CacheMixin.copyCache(self, src,dst)

    def fullcopyAsset(self, src, dst):
        '''
        copy a folder or a file, include archives
        keep stat
        '''
        if self.isfile(src):
            self.copyfile(src, dst)
        else:
            self.copytree(src, dst)

        frsSrc = self.frspath(src)
        if self.exists(frsSrc):
            frsDst = self.frspath(dst)
            frsDstDir = self.dirname(frsDst)
            if not self.exists(frsDstDir):
                self.makedirs(frsDstDir)
            self.copytree(frsSrc, frsDst)
