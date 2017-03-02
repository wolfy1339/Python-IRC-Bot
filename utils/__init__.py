# pylint: disable=unused-import
from . import util
from . import irc
# pylint: enable=unused-import

sysver = "".join(__import__("sys").version.split("\n"))
gitver = __import__("subprocess").check_output(['git',
                                                'rev-parse',
                                                '--short',
                                                'HEAD']).decode().split()[0]
version = "A zIRC bot v{0}@{1}, running on Python {2}".format("0.1",
                                                              gitver,
                                                              sysver)
