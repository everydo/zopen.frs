#coding:utf8
from config import FRS_REMOVED_FOLDER_NAME
from utils import timetag, int2ascii, ascii2int
import datetime
import time

class RecycleMixin:
    """ trushcase enables mixin for file repository system 
    """

    def removedpath(self, path, timestamp):
        if type(timestamp) in [str, unicode]:
            timestamp = ascii2int(timestamp)
        root, subpath= path[1:].split('/', 1)
        removeName = "%s.%s" % ( int2ascii(int(timestamp)), int2ascii(hash(subpath)))
        return self.joinpath('/',root, FRS_REMOVED_FOLDER_NAME, removeName)

    def recycleAssets(self, path, srcNames,timestamp=None):
        """ remove file or tree to trush folder """
        removedPath = self.removedpath(path, timestamp)
        for name in srcNames:
            srcPath = self.joinpath(path, name)
            dstPath = self.joinpath(removedPath, name)
            # remove cache file
            self.removeCache(srcPath)
            # just move to recycle
            self.moveAsset(srcPath, dstPath)

    def listRemoves(self, path):
        """ retime remved timestamps """
        root, subpath= path[1:].split('/', 1)
        recyle = self.joinpath(root, FRS_REMOVED_FOLDER_NAME)

        removes = []
        root, subpath= path[1:].split('/', 1)
        pathhash = int2ascii(hash(subpath))
        
        for filename in self.listdir(recyle):
            timestamp , _pathhash = filename.split('.', 1)
            if _pathhash == pathhash:
                removes.append(timestamp)
        return removes

    def listRemovedAssets(self, path, timestamp):
        removedPath = self.removedpath(path, timestamp)
        return self.listdir(removedPath)

    def revertRemove(self, path, removeName, assetName, reset_parent=None, new_name=''):
        """ 恢复一个删除的文件 """
        removedPath = self.removedpath(path, removeName)
        src_name = assetName 
        srcPath = self.joinpath(removedPath, src_name)
        dst_name = src_name if not new_name else new_name
        if reset_parent:
            dst_name = self.getNewName(reset_parent, dst_name)
            dstPath = self.joinpath(reset_parent, dst_name)
        else:
            dst_name = self.getNewName(path, dst_name)
            dstPath = self.joinpath(path, dst_name)

        self.moveAsset(srcPath, dstPath)

        # 已经全部恢复，删除这个文件夹
        if not self.listdir(removedPath):
            self.rmtree(removedPath)
        return dst_name

    def realRemove(self, path, removeName, assetNames=[]):
        removedPath = self.removedpath(path, removeName)
        if not self.exists(removedPath):
             return
        if not assetNames:
            self.rmtree(removedPath)
	    return 

        for name in assetNames:
            srcPath = self.joinpath(removedPath, name)
            self.removeAsset(srcPath)
        if not self.listdir(removedPath):
            self.rmtree(removedPath)

    def walkTrashBox(self, top_path='/', days=0, cmp_result=0):
        """ -1: older than history day; 0: all; 1: greater than history day 

        """
        # XXX need to rewrite
        cur_date = datetime.datetime(*time.gmtime()[:7])
        history_date = cur_date - datetime.timedelta(days)
        history_date_name = timetag(history_date)

        if top_path != '/':
            removeNames = self.listRemoves(top_path)
            if cmp_result != 0:
                removeNames = [removeName for removeName in removeNames
                            if cmp(removeName, history_date_name) == cmp_result]
            if removeNames:
                yield top_path, removeNames

        for parent_path, dirnames, filenames in self.walk(top_path):
            for dirname in dirnames:
                dir_vpath = self.joinpath(parent_path, dirname)
                removeNames = self.listRemoves(dir_vpath)
                if cmp_result != 0:
                    removeNames = [removeName for removeName in removeNames
                            if cmp(removeName, history_date_name) == cmp_result]
                if removeNames:
                    yield dir_vpath, removeNames

    def cleanTrushBox(self, top_path='/', days=30, cmp_result=-1):
        """ delete all items in trushboxes older than <keepDays> """
        for dir_vpath, remove_names in self.walkTrashBox(top_path, days, cmp_result):
            for remove_name in remove_names:
                self.realRemove(dir_vpath, remove_name)

