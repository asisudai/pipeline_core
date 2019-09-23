from __future__ import absolute_import
import logging as _logging
import sys
import time

try:
    import maya
    _in_maya = True
except ImportError:
    _in_maya = False

try:
    import nuke
    _in_nuke = True
except ImportError:
    _in_nuke = False

# globals
MSG_FORMAT  = '%(asctime)s %(name)s %(levelname)s : %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
GLOBAL_MUTE = False

# Levels - same as logging module
NOTSET   = 0
DEBUG    = 10
INFO     = 20
WARNING  = 30
ERROR    = 40
CRITICAL = 50


def getLogger(name, shell=True, maya=_in_maya, nuke=_in_nuke, file=None, level=INFO):
    '''
    Get logger instance

    Args:
        name    (str) : name.
        shell  (bool) : stout.
        maya   (bool) : maya output
        nuke   (bool) : nuke output.
        file    (str) : log filepath, for logging out to a file.
        level   (int) : logging level (10, 20, 30... )
    '''
    return Logger(name, shell, maya, nuke, file, level)


class Logger(object):
    '''
    Wrapper over built-in logger.
    '''

    def __init__(self, name, shell=True, maya=False, nuke=False, file=None, level=INFO):

        self.__name   = name
        self.__logger = _logging.getLogger(name)
        self.__logger.setLevel(level)
        self.__logger.propagate = False

        # if handlers exists, logger instance was already created.
        if self.__logger.handlers:
            return

        format = _logging.Formatter(MSG_FORMAT, DATE_FORMAT)

        if shell:
            stream_hdlr = ShellHandler()
            stream_hdlr.setFormatter(format)
            self.__logger.addHandler(stream_hdlr)

        if file:
            file_hdlr = _logging.FileHandler(file)
            file_hdlr.setFormatter(format)
            self.__logger.addHandler(file_hdlr)

        if maya and _in_maya:

            # in none-interactive mode skip this handler to avoid duplicate stdouts
            if not MayaHandler.in_batch():
                maya_hdlr = MayaHandler()
                maya_hdlr.setFormatter(format)
                self.__logger.addHandler(maya_hdlr)

        if nuke and _in_nuke:
            nuke_hdlr = NukeHandler()
            nuke_hdlr.setFormatter(format)
            self.__logger.addHandler(nuke_hdlr)

    def set_format(self, fmt=None, datefmt=None):
        '''
        Set all handlers format

            args:
                fmt     (str) : message format.
                datafmt (str) : datetime format.
        '''
        format = _logging.Formatter(fmt=fmt, datefmt=datefmt)
        for handler in self.__logger.handlers:
            handler.setFormatter(format)


    def __repr__(self):
        return '{}({} Level:{})'.format(self.__class__, self.__name, self.level)

    def __getattr__(self, attr):
        if hasattr(self.__logger, attr):
            return getattr(self.__logger, attr)
        else:
            raise AttributeError("No attribute {}".format(attr))

    ## LEVELS
    def debug(self, msg, inview_msg=False):
        self.__logger.debug(msg, extra={'inview_msg':inview_msg})

    def info(self, msg, inview_msg=False):
        self.__logger.info(msg, extra={'inview_msg':inview_msg})

    def warning(self, msg, inview_msg=False):
        self.__logger.warning(msg, extra={'inview_msg':inview_msg})

    def error(self, msg, inview_msg=False):
        self.__logger.error(msg, extra={'inview_msg':inview_msg})

    def critical(self, msg, inview_msg=False):
        self.__logger.critical(msg, extra={'inview_msg':inview_msg})


class ShellHandler(_logging.Handler):

    def __init__(self):
        _logging.Handler.__init__(self)


    def emit(self, record):
        if GLOBAL_MUTE == False:
            sys.__stdout__.write("%s\n" %self.format(record))


class MayaHandler(_logging.Handler):

    DELAY = None

    def __init__(self):
        _logging.Handler.__init__(self)

    def emit(self, record):
        if hasattr(record, 'inview_msg'):
            inview_msg = getattr(record, 'inview_msg')
        else:
            inview_msg = False

        msg = self.format(record)

        if record.funcName == "warning":
            maya.cmds.warning("\n"+msg)

        elif record.funcName in ["critical"]:

            sys.stdout.write("\n{}\n".format(msg))

            ## Open dialog if not in batch mode:
            if maya.cmds.about(batch=True) == False:

                maya.cmds.confirmDialog(title   = "{} has an error(s)".format(record.funcName),
                                        message = record.message,
                                        button  = ['Dismiss'],
                                        messageAlign = "left")

        else:
            sys.stdout.write(msg+"\n")

        ## If indicated or not in batch mode, display in viewport
        if maya.cmds.about(batch=True) == False and inview_msg:
            if not self.DELAY or (time.time() - self.DELAY) >= 2:
                maya.cmds.inViewMessage(message  = record.message,
                                        dragKill = True,
                                        position = "midCenterTop")
                self.DELAY = time.time()

    @staticmethod
    def in_batch():
        try:
            from maya import cmds
            # if in mayabatch or mayapy mode and maya wasn't initialize,
            # cmds module will be empty and will error out. that's a sign
            # we're in batch mode anyways, so return True
            return cmds.about(batch=True)
        except Exception:
            return True


class NukeHandler(_logging.Handler):

    def __init__(self):
        _logging.Handler.__init__(self)

    def emit(self, record):

        # Formated message:
        msg = self.format(record)

        if record.funcName == "warning":
            nuke.warning(msg)

        elif record.funcName in ["critical", "fatal"]:
            nuke.error(msg)
            nuke.message(record.message)

        else:
            sys.stdout.write(msg)

if __name__ == '__main__':
    LOG1 = getLogger('1st', level=DEBUG)
    LOG1.debug('log debug')
    LOG1.info('log info')
    LOG1.warning('log warning')
    LOG1.critical('log critical')

    # logger with different formats
    MSG_FORMAT2  = '%(name)s %(levelname)s : %(message)s'
    DATE_FORMAT2 = ''
    LOG2 = getLogger('2nd', level=INFO)
    LOG2.set_format(MSG_FORMAT2, DATE_FORMAT2)
    LOG2.info('log2 info')
