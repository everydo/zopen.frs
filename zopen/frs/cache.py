# encoding: utf-8
import os

from .config import FRS_CACHE_FOLDER_PREFIX

class CacheMixin:

    def getCacheFolder(self, vpath, cachename=None):
        """ get os path of cache folder for vpath """
        cachebase = os.path.join(self.cache_root, *vpath.split('/') )

        if cachename:
            foldername = FRS_CACHE_FOLDER_PREFIX + cachename
            return os.path.join(cachebase, foldername)
        else:
            return cachebase

    def getCacheDecompressFileVpath(self, vpath, cachename=None, subpath=''):
        return '/cache' + vpath + '/' + FRS_CACHE_FOLDER_PREFIX + cachename + '/decompress' + subpath

    # TODO remove
    def getCacheDecompress(self, vpath, cachename=None):
        """ get os path of cache decompress for vpath """
        return os.path.join(self.getCacheFolder(vpath, cachename), 'decompress')

    # TODO remove
    def getCacheDecompressPreview(self, vpath, cachename=None):
        """ get os path of cache decompress preview for vpath """
        return os.path.join(self.getCacheFolder(vpath, cachename), 'decompresspreview')

    def hasCache(self, vpath, cachename=None):
        return os.path.exists(self.getCacheFolder(vpath, cachename))

    def removeCache(self, vpath,cachename=None):
        while True:
            vpath = '/cache' + vpath
            if self.exists(vpath):
                self.rmtree(vpath)
            else:
                break

    def moveCache(self, src, dst):
        while True:
            src, dst = '/cache' + src, '/cache' + dst
            if self.exists(src):
                self.move(src, dst)
            else:
                break

    def copyCache(self, src, dst, **kw):
        while True:
            src, dst = '/cache' + src, '/cache' + dst
            if self.exists(src):
                if self.exists(dst):  # 有时候事务不干净，这个会存在
                    self.rmtree(dst)
                self.copytree(src, dst)
            else:
                break
