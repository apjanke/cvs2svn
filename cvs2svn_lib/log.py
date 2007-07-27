# (Be in -*- python -*- mode.)
#
# ====================================================================
# Copyright (c) 2000-2007 CollabNet.  All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.  The terms
# are also available at http://subversion.tigris.org/license-1.html.
# If newer versions of this license are posted there, you may use a
# newer version instead, at your option.
#
# This software consists of voluntary contributions made by many
# individuals.  For exact contribution history, see the revision
# history and logs, available at http://cvs2svn.tigris.org/.
# ====================================================================

"""This module contains a simple logging facility for cvs2svn."""


import sys
import time
import threading

from cvs2svn_lib.boolean import *


class Log:
  """A Simple logging facility.

  If self.log_level is DEBUG or higher, each line will be timestamped
  with the number of wall-clock seconds since the time when this
  module was first imported.

  If self.use_timestamps is True, each line will be timestamped with a
  human-readable clock time.

  The public methods of this class are thread-safe.

  This class is a Borg; see
  http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531."""

  # These constants represent the log levels that this class supports.
  # The increase_verbosity() and decrease_verbosity() methods rely on
  # these constants being consecutive integers:
  WARN = -1
  QUIET = 0
  NORMAL = 1
  VERBOSE = 2
  DEBUG = 3

  start_time = time.time()

  __shared_state = {}

  def __init__(self):
    self.__dict__ = self.__shared_state
    if self.__dict__:
      return
    self.log_level = Log.NORMAL
    # Set this to True if you want to see timestamps on each line output.
    self.use_timestamps = False
    self.logger = sys.stdout
    # Lock to serialize writes to the log:
    self.lock = threading.Lock()

  def increase_verbosity(self):
    self.lock.acquire()
    try:
      self.log_level = min(self.log_level + 1, Log.DEBUG)
    finally:
      self.lock.release()

  def decrease_verbosity(self):
    self.lock.acquire()
    try:
      self.log_level = max(self.log_level - 1, Log.WARN)
    finally:
      self.lock.release()

  def is_on(self, level):
    """Return True iff messages at the specified LEVEL are currently on.

    LEVEL should be one of the constants Log.WARN, Log.QUIET, etc."""

    return self.log_level >= level

  def _timestamp(self):
    """Return a timestamp if needed, as a string with a trailing space."""

    retval = []

    if self.log_level >= Log.DEBUG:
      retval.append('%f: ' % (time.time() - self.start_time,))

    if self.use_timestamps:
      retval.append(time.strftime('[%Y-%m-%d %I:%M:%S %Z] - '))

    return ''.join(retval)

  def write(self, *args):
    """Write a message to the log.

    This is the public method to use for writing to a file.  If there
    are multiple ARGS, they will be separated by spaces.  If there are
    multiple lines, they will be output one by one with the same
    timestamp prefix."""

    timestamp = self._timestamp()
    s = ' '.join(map(str, args))
    lines = s.split('\n')
    if lines and not lines[-1]:
      del lines[-1]

    self.lock.acquire()
    try:
      for s in lines:
        self.logger.write('%s%s\n' % (timestamp, s,))
      # Ensure that log output doesn't get out-of-order with respect to
      # stderr output.
      self.logger.flush()
    finally:
      self.lock.release()

  def warn(self, *args):
    """Log a message at the WARN level."""

    if self.is_on(Log.WARN):
      self.write(*args)

  def quiet(self, *args):
    """Log a message at the QUIET level."""

    if self.is_on(Log.QUIET):
      self.write(*args)

  def normal(self, *args):
    """Log a message at the NORMAL level."""

    if self.is_on(Log.NORMAL):
      self.write(*args)

  def verbose(self, *args):
    """Log a message at the VERBOSE level."""

    if self.is_on(Log.VERBOSE):
      self.write(*args)

  def debug(self, *args):
    """Log a message at the DEBUG level."""

    if self.is_on(Log.DEBUG):
      self.write(*args)


