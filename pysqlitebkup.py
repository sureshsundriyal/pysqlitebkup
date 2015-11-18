#! /usr/bin/env python

import ctypes
from ctypes.util import find_library

__author__ = 'Suresh Sundriyal'
__copyright__ = 'Copyright (c) 2015, Suresh Sundriyal'
__license__ = 'ISC License (ISC)'
__version__ = '0.0.1'
__credits__ = [ 'Joongi Kim (achimnol)' ]

SQLITE_OK = 0
SQLITE_ERROR = 1
SQLITE_BUSY = 5
SQLITE_LOCKED = 6
SQLITE_DONE = 101

SQLITE_OPEN_READONLY = 1
SQLITE_OPEN_READWRITE = 2
SQLITE_OPEN_CREATE = 4

sqlite = ctypes.CDLL(find_library('sqlite3'))
sqlite.sqlite3_backup_init.restype = ctypes.c_void_p

class BackupInitException(Exception):
    pass

class BackupFailedException(Exception):
    pass

class FileOpenException(Exception):
    pass

class UninitializedException(Exception):
    pass

class dbbackup(object):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self.p_src_db = ctypes.c_void_p(None)
        self.p_dst_db = ctypes.c_void_p(None)
        self.p_backup = ctypes.c_void_p(None)
        self.finished = False
        self.remaining = None
        self.pagecount = None

    def __enter__(self):
        self.backupInit()
        return self

    def __exit__(self, type, value, traceback):
        self.backupFinish()

    def backupInit(self):

        files = { self.src : (self.p_src_db, SQLITE_OPEN_READONLY),
                  self.dst : (self.p_dst_db,
                              SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE) }

        for fileName, ptrMode  in list(files.items()):
            fileName = ctypes.c_char_p(fileName.encode('utf-8'))
            rc = sqlite.sqlite3_open_v2(fileName, ctypes.byref(ptrMode[0]),
                                    ptrMode[1], None)
            if (rc != SQLITE_OK or ptrMode[0].value is None):
                raise FileOpenException("Unable to open file(%s), rc(%s)" % (
                                        fileName, rc))

        dbType = 'main'.encode('utf-8')
        self.p_backup = ctypes.c_void_p(sqlite.sqlite3_backup_init(
                                                   self.p_dst_db, dbType,
                                                   self.p_src_db, dbType))
        if self.p_backup.value is None:
            raise BackupInitException("Failed to backup_init")

    def backupFinish(self):

        if self.p_backup.value is not None:
            sqlite.sqlite3_backup_finish(self.p_backup)

        rc = sqlite.sqlite3_errcode(self.p_dst_db)

        if self.p_dst_db.value is not None:
            sqlite.sqlite3_close(self.p_dst_db)
        if self.p_src_db.value is not None:
            sqlite.sqlite3_close(self.p_src_db)

        if rc != SQLITE_OK:
            raise BackupFailedException("Failed to backup db: rc(%s)" % rc)

    def step(self, size=5):
        if self.p_backup.value is None:
            raise UninitializedException(
                    "step called without calling backupInit first")

        rc = sqlite.sqlite3_backup_step(self.p_backup, size)
        self.remaining = sqlite.sqlite3_backup_remaining(self.p_backup)
        self.pagecount = sqlite.sqlite3_backup_pagecount(self.p_backup)

        if self.remaining == 0:
            self.finished = True

        if rc in (SQLITE_OK, SQLITE_BUSY, SQLITE_LOCKED):
            # sleep for 250 ms before continuing.
            sqlite.sqlite3_sleep(250)

if __name__ == '__main__':
    import sys
    import logging
    try:
        with dbbackup(sys.argv[1], sys.argv[2]) as p:
            while not p.finished:
                p.step(20)
    except:
        logging.exception("Failed to backup sqlite db")