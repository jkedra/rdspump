import argparse


def cli_parser() -> argparse.ArgumentParser:
    """
    https://docs.python.org/3/howto/argparse.html
    https://docs.python.org/3/library/argparse.html#module-argparse
    Returns argparse.Namespace object.
    """
    p: argparse.ArgumentParser = argparse.ArgumentParser()
    p.add_argument("-l", "--list-profiles", nargs='?',
                   default=argparse.SUPPRESS, const='ListAll')
    p.add_argument("-P", "--profile",
                   default=argparse.SUPPRESS,
                   help="profile from the configuration file")

    subparsers = p.add_subparsers(help="subcommands menu",
                                  dest='subparser_name')

    # GET
    # download a file from db
    p_get = subparsers.add_parser("get", help="download a file")

    # p_get.add_argument("user")
    # p_get.add_argument("password")
    p_get.add_argument("directory", nargs='?',
                       default=argparse.SUPPRESS,
                       help="oracle directory")
    p_get.add_argument("file",
                       help="filename to download from database")
    p_get.add_argument("-z", action="store_true",
                       help="gzip resulting file inline")

    # PUT
    # upload a file from a local filesystem
    p_put = subparsers.add_parser("put", help="upload a file")
    p_put.add_argument("directory", nargs='?',
                       default=argparse.SUPPRESS,
                       help="oracle directory")
    p_put.add_argument("file",
                       help="filename to upload into database")

    # DEL
    # remove a file from db
    p_rm = subparsers.add_parser("del", help="delete a file")
    p_rm.add_argument("directory", nargs='?',
                      default=argparse.SUPPRESS,
                      help="oracle directory")
    p_rm.add_argument("file",
                      help="remove file from database")

    return p
