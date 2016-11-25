###
# Copyright (c) 2002-2005, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import os
import sys
import time
import atexit
import logging
import operator
import textwrap
import threading
import traceback

import config
import six
import ansi


###
# supybot.utils.gen
###
def exnToString(exn):
    """Turns a simple exception instance into a string (better than str(e))"""
    strE = str(exn)
    if strE:
        return '{0!s}: {1!s}'.format(exn.__class__.__name__, strE)
    else:
        return exn.__class__.__name__


def stackTrace(frame=None, compact=True):
    if frame is None:
        frame = sys._getframe()
    if compact:
        L = []
        while frame:
            lineno = frame.f_lineno
            funcname = frame.f_code.co_name
            filename = os.path.basename(frame.f_code.co_filename)
            L.append('[{0!s}|{1!s}|{2!s}]'.format(filename, funcname, lineno))
            frame = frame.f_back

        return textwrap.fill(' '.join(L))
    else:
        return traceback.format_stack(frame)
###
# supybot.utils.python
###
import types

def changeFunctionName(f, name, doc=None):
    if doc is None:
        doc = f.__doc__

    if hasattr(f, '__closure__'):
        closure = f.__closure__
    else:
        # Pypy
        closure = f.func_closure
    newf = types.FunctionType(f.__code__, f.__globals__, name,
                              f.__defaults__, closure)
    newf.__doc__ = doc
    return newf

class Object(object):
    def __ne__(self, other):
        return not self == other

class MetaSynchronized(type):
    METHODS = '__synchronized__'
    LOCK = '_MetaSynchronized_rlock'

    def __new__(mcs, name, bases, dictionnary):
        sync = set()
        for base in bases:
            if hasattr(base, MetaSynchronized.METHODS):
                sync.update(getattr(base, MetaSynchronized.METHODS))

        if MetaSynchronized.METHODS in dictionnary:
            sync.update(dictionnary[MetaSynchronized.METHODS])

        if sync:
            def synchronized(f):
                def g(self, *args, **kwargs):
                    lock = getattr(self, MetaSynchronized.LOCK)
                    lock.acquire()

                    try:
                        f(self, *args, **kwargs)
                    finally:
                        lock.release()

                return changeFunctionName(g, f.__name__, f.__doc__)

            for attr in sync:
                if attr in dictionnary:
                    dict[attr] = synchronized(dictionnary[attr])
            original__init__ = dictionnary.get('__init__')

            def __init__(self, *args, **kwargs):
                if not hasattr(self, MetaSynchronized.LOCK):
                    setattr(self, MetaSynchronized.LOCK, threading.RLock())

                if original__init__:
                    original__init__(self, *args, **kwargs)
                else:
                    # newclass is defined below.
                    super(MetaSynchronized, self).__init__(*args, **kwargs)

            dictionnary['__init__'] = __init__
        newclass = super(MetaSynchronized, mcs).__new__(mcs, name, bases, dictionnary)

        return newclass
Synchronized = MetaSynchronized('Synchronized', (), {})

deadlyExceptions = [KeyboardInterrupt, SystemExit]

###
# This is for testing, of course.  Mostly it just disables the firewall code
# so exceptions can propagate.
###
testing = False


class Formatter(logging.Formatter):
    _fmtConf = config.logFormat

    def formatTime(self, record, datefmt=None):
        return timestamp(record.created)

    def formatException(self, exc_info):
        (Exc, er, tb) = exc_info
        for exn in deadlyExceptions:
            if issubclass(er.__class__, exn):
                raise
        return logging.Formatter.formatException(self, (Exc, er, tb))

    def format(self, record):
        self._fmt = self._fmtConf
        if hasattr(self, '_style'):  # Python 3
            self._style._fmt = self._fmtConf
        return logging.Formatter.format(self, record)


class PluginFormatter(Formatter):
    _fmtConf = config.logFormat


class Logger(logging.Logger):
    def exception(self, *args):
        (E, er, tb) = sys.exc_info()
        del er
        tbinfo = traceback.extract_tb(tb)
        path = '[{0!s}]'.format('|'.join(map(operator.itemgetter(2), tbinfo)))
        eStrId = '{0!s}:{1!s}'.format(E, path)
        eId = hex(hash(eStrId) & 0xFFFFF)
        logging.Logger.exception(self, *args)
        self.error('Exception id: %s', eId)
        # The traceback should be sufficient if we want it.
        # self.error('Exception string: %s', eStrId)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        msg = msg % tuple(args)
        logging.Logger._log(self, level, msg, (), exc_info=exc_info,
                            extra=extra)


class StdoutStreamHandler(logging.StreamHandler):
    def format(self, record):
        s = logging.StreamHandler.format(self, record)
        if record.levelname != 'ERROR' and config.stdoutWrap:
            # We check for ERROR there because otherwise, tracebacks (which are
            # already wrapped by Python itself) wrap oddly.
            if not isinstance(record.levelname, six.string_types):
                print(record)
                print(record.levelname)
                print(stackTrace())
            prefixLen = len(record.levelname) + 1  # ' '
            s = textwrap.fill(s, width=78, subsequent_indent=' '*prefixLen)
            s.rstrip('\r\n')
        return s

    def emit(self, record):
        try:
            logging.StreamHandler.emit(self, record)
        except ValueError:  # Raised if sys.stdout is closed.
            self.disable()
            error('Error logging to stdout.  Removing stdout handler.')
            exception('Uncaught exception in StdoutStreamHandler:')

    def disable(self):
        self.setLevel(sys.maxsize)  # Just in case.
        _logger.removeHandler(self)
        logging._acquireLock()
        try:
            del logging._handlers[self]
        finally:
            logging._releaseLock()


class BetterFileHandler(logging.FileHandler):
    def emit(self, record):
        msg = self.format(record)
        try:
            self.stream.write(msg)
        except (UnicodeError, TypeError):
            try:
                self.stream.write(msg.encode("utf8"))
            except (UnicodeError, TypeError):
                try:
                    self.stream.write(msg.encode("utf8").decode('ascii',
                                                                'replace'))
                except (UnicodeError, TypeError):
                    self.stream.write(repr(msg))
        self.stream.write(os.linesep)
        try:
            self.flush()
        except OSError as e:
            if e.args[0] == 28:
                print('No space left on device, cannot flush log.')
            else:
                raise


class ColorizedFormatter(Formatter):
    # This was necessary because these variables aren't defined until later.
    # The staticmethod is necessary because they get treated like methods.
    _fmtConf = config.logFormat

    def formatException(self, exc_info):
        (E, exn, tb) = exc_info
        if config.colorized:
            return ''.join([ansi.RED,
                            Formatter.formatException(self, (E, exn, tb)),
                            ansi.RESET])
        else:
            return Formatter.formatException(self, (E, exn, tb))

    def format(self, record, *args, **kwargs):
        if config.colorized:
            color = ''
            if record.levelno == logging.CRITICAL:
                color = ansi.WHITE + ansi.BOLD
            elif record.levelno == logging.ERROR:
                color = ansi.RED
            elif record.levelno == logging.WARNING:
                color = ansi.YELLOW
            if color:
                return ''.join([color,
                                Formatter.format(self, record, *args, **kwargs),
                                ansi.RESET])
            else:
                return Formatter.format(self, record, *args, **kwargs)
        else:
            return Formatter.format(self, record, *args, **kwargs)


try:
    messagesLogFilename = 'messages.log'
    _handler = BetterFileHandler(messagesLogFilename, encoding='utf8')
except EnvironmentError as e:
    raise SystemExit('Error opening messages logfile (%s).  ' \
          'Generally, this is because you are running Supybot in a directory ' \
          'you don\'t have permissions to add files in, or you\'re running ' \
          'Supybot as a different user than you normal do.  The original ' \
          'error was: %s' % (messagesLogFilename, exnToString(e)))

# These are public.
formatter = Formatter('NEVER SEEN; IF YOU SEE THIS, FILE A BUG!')
pluginFormatter = PluginFormatter('NEVER SEEN; IF YOU SEE THIS, FILE A BUG!')

# These are not.
logging.setLoggerClass(Logger)
_logger = logging.getLogger('bot')
_stdoutHandler = StdoutStreamHandler(sys.stdout)

# These just make things easier.
debug = _logger.debug
info = _logger.info
warning = _logger.warning
error = _logger.error
critical = _logger.critical
exception = _logger.exception

setLevel = _logger.setLevel

atexit.register(logging.shutdown)


def timestamp(when=None):
    if when is None:
        when = time.time()
    t = time.localtime(when)
    return time.strftime(config.timestampFormat, t)


def firewall(f, errorHandler=None):
    def logException(self, s=None):
        if s is None:
            s = 'Uncaught exception'
        if hasattr(self, 'log'):
            logging_function = self.log.exception
        else:
            logging_function = exception
        logging_function('%s in %s.%s:', s, self.__class__.__name__,
                         f.__name__)

    def m(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception:
            if testing:
                raise
            logException(self)
            if errorHandler is not None:
                try:
                    return errorHandler(self, *args, **kwargs)
                except Exception:
                    logException(self, 'Uncaught exception in errorHandler')
    m = changeFunctionName(m, f.__name__, f.__doc__)
    return m


class MetaFirewall(type):
    def __new__(mcs, name, bases, classdict):
        firewalled = {}
        for base in bases:
            if hasattr(base, '__firewalled__'):
                mcs.updateFirewalled(firewalled, base.__firewalled__)
        mcs.updateFirewalled(firewalled, classdict.get('__firewalled__', []))
        for (attr, errorHandler) in firewalled.items():
            if attr in classdict:
                classdict[attr] = firewall(classdict[attr], errorHandler)
        return super(MetaFirewall, mcs).__new__(mcs, name, bases, classdict)

    @classmethod
    def getErrorHandler(mcs, dictOrTuple, name):
        if isinstance(dictOrTuple, dict):
            return dictOrTuple[name]
        else:
            return None

    @classmethod
    def updateFirewalled(mcs, firewalled, __firewalled__):
        for attr in __firewalled__:
            firewalled[attr] = mcs.getErrorHandler(__firewalled__, attr)
Firewalled = MetaFirewall('Firewalled', (), {})


_handler.setFormatter(formatter)

_handler.setLevel(config.logLevel)
_logger.addHandler(_handler)
_logger.setLevel(-1)

_stdoutFormatter = ColorizedFormatter('IF YOU SEE THIS, FILE A BUG!')
_stdoutHandler.setFormatter(_stdoutFormatter)
_stdoutHandler.setLevel(config.logLevel)
_logger.addHandler(_stdoutHandler)


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
