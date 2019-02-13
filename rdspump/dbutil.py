import os

from . import Params
from jxa.Progress import Progress
import time
from cx_Oracle import connect, DatabaseError, BLOB


def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


class DBUtil:

    def __init__(self, params: Params.Params):
        self.params = params

        # print(f"TNS: {params.ora.getdsn()}")
        # print(params.ora)

        o = params.ora
        self.conn = connect(o.user, o.password, o.getdsn())
        # todo: Progress value move to configuration
        # todo: add Progress flag to command line options
        self.progress = Progress(30)

    def dump_dir_exists(self):
        execute = self.conn.cursor().execute
        query = ("SELECT COUNT(*) FROM dba_directories WHERE "
                 "directory_name = :dir")
        (cnt,) = execute(query, dir=self.params.ora_dir).fetchone()

        if cnt == 1:
            return True
        else:
            return False

    def bfile_exists(self, fname=None) -> bool:

        assert self.params.fname
        assert self.params.ora_dir

        if fname:
            self.params.fname = fname
        execute = self.conn.cursor().execute
        if self.dump_dir_exists():
            query = "SELECT BFILENAME(:dir, :fname) FROM dual"
            (myLOB,) = execute(query, dir=self.params.ora_dir,
                               fname=self.params.fname).fetchone()
            return myLOB.fileexists()
        else:
            raise ValueError(f"Not existing directory {self.params.ora_dir}")

    def bfile_delete(self, fname=None):
        if fname:
            self.params.fname = fname

        if self.bfile_exists():
            proc = self.conn.cursor().callproc
            proc('utl_file.fremove', [self.params.ora_dir, self.params.fname])
        else:
            raise ValueError(f"Not existing file: {self.params.fname}")

    def bfile_upload(self, local_fn: str,
                     remote_fn: str = None,
                     chunk_size=32528):
        if not remote_fn: remote_fn = local_fn

        if self.bfile_exists():
            self.bfile_delete()

        # temporary name with second resolution
        seconds = int(time.time()) - 1554297340
        pkg_temp_name = f"DUMPGLOBAL{seconds}"
        glob_plsql_var = f"{pkg_temp_name}.FH"

        file_open = (f"BEGIN {glob_plsql_var} := UTL_FILE.FOPEN("
                     f"'{self.params.ora_dir}', '{remote_fn}', "
                     f"'wb', {chunk_size}); END;")

        file_write = f"BEGIN UTL_FILE.PUT_RAW({glob_plsql_var} , :lob , true); END;"
        file_close = f"BEGIN UTL_FILE.FCLOSE({glob_plsql_var}); END;"
        glob_proc = (f"CREATE OR REPLACE PACKAGE {pkg_temp_name} "
                     " AS fh UTL_FILE.FILE_TYPE; END;")
        drop_pkg = f"DROP PACKAGE {pkg_temp_name}"

        conn = self.conn
        cr = self.conn.cursor()
        cr.execute(glob_proc)
        cr.execute(file_open)

        try:
            file_size = os.path.getsize(local_fn)
            progress = self.progress
            with open(local_fn, mode='rb') as fd:
                mlob = conn.createlob(BLOB)
                cr.setinputsizes(lob=BLOB)
                print(f"lobchunksize {mlob.getchunksize()}")
                humansize = self.progress.human_readable_byte_count
                print(f"Uploading {humansize(file_size)}")

                bytes_uploaded = 0
                for chunk in read_in_chunks(fd, chunk_size):
                    mlob.trim()
                    mlob.write(chunk)
                    cr.execute(file_write, lob=mlob)
                    bytes_uploaded += len(chunk)
                    progress.print(bytes_uploaded, file_size, "Uploaded")
                progress.print_final(bytes_uploaded, file_size, "Completed")

        except DatabaseError as e:
            cr.execute(file_close)
            cr.execute(drop_pkg)
            raise e

    def bfile_download(self, remote_fn: str,
                       local_fn: str = None,
                       chunk_size=32528):

        local_fn = remote_fn if not local_fn else local_fn
        progress = self.progress
        cr = self.conn.cursor()

        mlob: BLOB
        query = "SELECT BFILENAME(:dir, :fname) FROM dual"
        qpars = {'dir': self.params.ora_dir, 'fname': remote_fn}
        (mlob,) = cr.execute(query, qpars).fetchone()

        lob_size = mlob.size()
        lob_size_str = progress.human_readable_byte_count(lob_size)
        print(f"lob size: {lob_size_str}")

        offset = 1
        with open(local_fn, mode='wb') as fd:
            while offset < lob_size:
                buff = mlob.read(offset, chunk_size)
                fd.write(buff)
                offset += len(buff)
                progress.print(offset - 1, lob_size)

        progress.print_final(offset - 1, lob_size, "Completed")
