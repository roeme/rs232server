#!/usr/bin/python2

# Copyright (C) 2011,2012 Brendan Le Foll <brendan@fridu.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import gobject
import argparse
import logging
import dbus
import Shared
from dbus.mainloop.glib import DBusGMainLoop
from BaseService import BaseService, invalidtty
#from azur_service import AzurService
#from lgtv_service import LgtvService
import ConfigParser

LOG_FILENAME = '/tmp/' + Shared.APP_NAME + '.log'
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
RS232SERVER_BUS_NAME = 'uk.co.madeo.' + Shared.APP_NAME
DESCRIPTION = "Listen over dbus for commands to be sent over RS232"

def configureLogging(verbose, logger):
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter(LOG_FORMAT)
  try:
    fh = logging.FileHandler(LOG_FILENAME)
  except:
    print 'Check you have write permissions to', LOG_FILENAME
    exit(1)
  fh.setLevel(logging.DEBUG)
  fh.setFormatter(formatter)
  logger.addHandler(fh)
  ch = logging.StreamHandler()
  if verbose:
    ch.setLevel(logging.DEBUG)
  else:
    ch.setLevel(logging.ERROR)
  ch.setFormatter(formatter)
  logger.addHandler(ch)

def main():
  # parse CLI arguments
  parser = argparse.ArgumentParser(description=DESCRIPTION)
  parser.add_argument('--verbose', '-v', action='store_true', dest='verbose', default=False,
                      help='enables more verbose output')
  parser.add_argument('--development', '-dev', action='store_true', dest='dev', default=False,
                      help='development mode disables some commands that could be dangerous. Read documentation before using')
  args = parser.parse_args()

  # set up logging
  logger = logging.getLogger(Shared.APP_NAME)
  configureLogging(args.verbose, logger)

  # read configuration file
  parser = ConfigParser.SafeConfigParser()
  try:
    parser.readfp(open(Shared.CONF_PATH))
  except:
    logger.error('failed to read ' + Shared.CONF_PATH)
    exit(1)

  # start dbus mainloop
  DBusGMainLoop(set_as_default=True)
  try:
    bus_name = dbus.service.BusName(RS232SERVER_BUS_NAME, bus=dbus.SystemBus())
  except:
    logger.error('fatal dbus error')
    exit(1)

  for section in parser.sections():
    try:
      tty = parser.get(section, 'tty')
      x = __import__(section)
      service = eval('x.' + section)(tty,bus_name)
      #if not issubclass(service, BaseService): 
      #  raise Exception("Class is not subclass of BaseService")
    except ConfigParser.NoOptionError, err:
      logger.error('%s in %s', str(err), Shared.CONF_PATH)
      exit(1)
    except invalidtty, e:
      logger.error('%s', str(e))
      exit(1)
    except Exception, e:
      logger.debug('%s', str(e))
      logger.error('Check that %s is a valid service name', section)
      exit(1)

  loop = gobject.MainLoop()
  loop.run()

if __name__ == "__main__":
    sys.exit(main())
