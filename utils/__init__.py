# pylint: disable=unused-import
from . import commands
from . import database
from . import ignores
from . import irc
from . import tasks
from . import util
from . import web
# pylint: enable=unused-import

sysver = "".join(__import__("sys").version.split("\n"))
gitver = __import__("subprocess").check_output(['git',
                                                'rev-parse',
                                                '--short',
                                                'HEAD']).decode().split()[0]
ver = "0.1"
version = f"A zIRC bot v{ver}@{gitver}, running on Python {sysver}"
