import argparse
import configparser
from jxa.genmixin import ReprMixin
from enum import Enum
from typing import Union

Mode = Enum('ProgramMode', 'GET PUT DEL NONE')
ModeT = Union[Mode, str]


class OraPar(ReprMixin):
    """ Reflects Oracle connection parameters only.
    """
    _attrs_filter = 'user password port sid service address dsn'.split()
    _attrs_ignore_empty = True

    def __init__(self, user=None, password=None, port=1521, sid=None,
                 service=None, address=None, dsn=None):
        """

        :param dsn:  The dsn (data source name) is the TNS entry.
        """

        self.user = user
        self.password = password

        self.port = port
        self.sid = sid
        self.service = service
        self.address = address

        # The dsn (data source name) is the TNS entry (from the Oracle names
        # server or tnsnames.ora file) or is a string like the one returned
        # from makedsn().
        if dsn:
            self.setdsn(dsn)
        else:
            self.dsn = None

    def setdsn(self, dsn):

        self.dsn = dsn
        self.port = None
        self.sid = None
        self.service = None
        self.address = None

    def getdsn(self):
        assert self.user
        assert self.password
        assert self.address
        assert self.service or self.address

        host = f" (HOST={self.address})" if self.address else ''
        port = f" (PORT={self.port})" if self.port else '(PORT=1521)'
        service = f" (SERVICE_NAME={self.service})" if self.service else ''
        sid = f" (SID={self.sid})" if self.sid else ''

        self.dsn = (f"(DESCRIPTION= (ADDRESS= (PROTOCOL=TCP){host}{port}) "
                    f"(CONNECT_DATA= (SERVER=dedicated){service}{sid}))")

        return self.dsn


class Params(ReprMixin):
    """ Reflects parameters from configuration and command line.
    """

    _attrs_filter = 'profile ora_dir mode ora'.split()
    _attrs_ignore_empty = True

    def __str__(self) -> str:
        return super().__str__()

    def __init__(self):
        self.profile = None
        self.ora_dir = None  # dump directory
        self.fname = None    # dump file name

        self.ora = OraPar()

        # ArgParser or CfgParser already used to initialize Params
        self._cfgparse: configparser.ConfigParser = None
        self._argparse = None

    def init_from_args(self, args: argparse.Namespace):
        """ initialize from argparse(commandline options)
            argparse.Namespace is a class defining object holding attributes.
        """
        self._argparse = args

        if hasattr(args, 'profile'):
            self.profile = args.profile
            self.init_from_cfg_profile(self.profile)

        if hasattr(args, 'list_profiles'):
            self.list_profiles(args.list_profiles)
            exit(-1)

        if hasattr(args, 'directory'):
            self.ora_dir = args.directory

        if self.mode() in [Mode.GET, Mode.DEL, Mode.PUT]:
            self.fname = args.file

    def list_profiles(self, profile):
        cfgparse = self._cfgparse
        if cfgparse:
            if profile == 'ListAll':
                for section in cfgparse.sections():
                    print(section)
            else:
                if profile in cfgparse.sections():
                    for (name, value) in self._cfgparse[profile].items():
                        print(f"{name}: {value}")
                else:
                    print(f"Not Found: {profile}")

    def init_from_cfg_profile(self, profile):
        """ update from specific profile """
        assert self._cfgparse

        if profile not in self._cfgparse.sections():
            print(f"No such profile {profile}")
            exit(-1)

        ora = self.ora
        self.profile = profile

        def getprof(attr, fallback):
            return self._cfgparse.get(self.profile, attr, fallback=fallback)

        ora.user = getprof('user', ora.user)
        ora.password = getprof('password', ora.password)
        ora.port = getprof('port', ora.port)
        ora.sid = getprof('sid', ora.sid)
        ora.service = getprof('service', ora.service)
        ora.address = getprof('address', ora.address)
        ora.dsn = getprof('dsn', ora.dsn)
        self.ora_dir = getprof('directory', self.ora_dir)

    def init_from_cfg(self, cfg: configparser.ConfigParser) -> 'Params':
        """ initializes from ConfigParser

        :param cfg: ConfigParser object
        :return:
        """

        def getdef(attr, fallback):
            return cfg.get('DEFAULT', attr, fallback=fallback)

        self._cfgparse = cfg
        ora = self.ora

        self.profile = getdef('profile', None)
        self.ora_dir = getdef('directory', None)

        ora.user = getdef('user', ora.user)
        ora.password = getdef('password', ora.password)
        ora.port = getdef('port', ora.port)
        ora.sid = getdef('sid', ora.sid)
        ora.service = getdef('service', ora.service)

        if self.profile:
            self.init_from_cfg_profile(self.profile)

        return self

    def mode(self) -> ModeT:
        switcher = {'get': Mode.GET,
                    'put': Mode.PUT,
                    'del': Mode.DEL
                    }
        return switcher.get(self._argparse.subparser_name, Mode.NONE)

    def print_usage(self):
        if self._argparse:
            self._argparse.print_usage()
        else:
            raise AssertionError
