import argparse
import configparser
import os
import sys

from . import cmdparser
from .Params import Params, Mode
from .dbutil import DBUtil

DEBUG = False


class RDSDumpParHelp(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        if args is not None:
            self.message = args[0]


def core(params: Params):
    try:
        if params.mode() == Mode.GET:
            db = DBUtil(params)
            db.bfile_download(params.fname, params.fname)

        if params.mode() == Mode.PUT:
            db = DBUtil(params)
            db.bfile_upload(params.fname)

        if params.mode() == Mode.DEL:
            db = DBUtil(params)
            db.bfile_delete()

        if params.mode() == Mode.NONE:
            raise RDSDumpParHelp("At least one argument expected.")

    except ValueError as e:
        print(f"Runtime Error: {e}")


def entry_point():
    params: Params = Params()

    cfg = configparser.ConfigParser()
    cfgfiles = ['rdspump.cfg', os.path.expanduser('~/.rdspump.cfg')]
    cfgfilesread = cfg.read(cfgfiles)

    if len(cfgfilesread) == 0:
        print("config file not found")
        sys.exit(-1)
    else:
        params.init_from_cfg(cfg)

    argparser: argparse.ArgumentParser = cmdparser.cli_parser()
    argparsed: argparse.Namespace = argparser.parse_args()

    params.init_from_args(argparsed)

    try:
        core(params)
    except RDSDumpParHelp as e:
        print(e)
        argparser.print_usage()


if __name__ == "__main__":
    entry_point()
