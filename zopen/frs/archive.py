# -*- encoding: utf-8 -*-
""" asset archive management
"""

from config import FRS_ARCHIVED_FOLDER_NAME


class ArchiveSupportMixin:

    def archivedpath(self, path, *args):
        return self.frspath(path, FRS_ARCHIVED_FOLDER_NAME, *args)

    def archive(self, path, id):
        archivePath = self.archivedpath(path)
        if not self.exists(archivePath):
            self.makedirs(archivePath)

        dstpath = self.joinpath(archivePath, id)
        self.copyAsset(path, dstpath, copycache=0)

    def listArchives(self, path):
        archivePath = self.archivedpath(path)
        if self.exists(archivePath):
            archives = self.listdir(archivePath)
        else:
            archives = []
        return archives

    def copyArchive(self, path, archiveName, dstPath):
        assetpath = self.archivedpath(path, archiveName)
        return self.copyAsset(assetpath, dstPath, copycache=0)

    def removeArchive(self, path, archiveName):
        self.removeAsset( self.archivedpath(path, archiveName) )

