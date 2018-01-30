#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:set noet:

from __future__ import division, print_function, with_statement
import serial
import io
import logging
from datetime import datetime

class GPSClock(object):

	FAULTS = {
		1: 'Drift Limit Fault',
		2: 'Reference Fault',
		4: 'GPS Communication Fault',
		8: 'GPS Antenna Fault',
		16: 'Oscillator Control Fault',
		32: 'GPS Battery Fault'
	}

	def __init__(self, port):
		# Start logger:
		self.logger = logging.getLogger(__name__)
		self.logger.debug('Setting up serial connection')

		# Open serial connection to clock:
		self.ser = serial.Serial(port=port, baudrate=9600, parity=serial.PARITY_NONE, timeout=1.0)
		self.io = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 1),
                               newline = '\n',
                               line_buffering = True)

		# Make sure we are using the right settings:
		self.SendAndRecieve('ECHO,0') # Turn echoing of commands off
		self.SendAndRecieve('TMODE,0') # 0=UTC, 1=GPS, 2=LOCAL
		self.SendAndRecieve('DSTSTATE,0') # Disable Daylight Savings Time
		self.SendAndRecieve('PPMODE,0') # Disable Programmable Pulse

		# Check for faults:
		faults = self.faults
		if faults is not None:
			self.logger.error("Faults: %s", faults)

		self.logger.debug("init done")

	def close(self):
		self.ser.close()

	def __enter__(self, *args, **kwargs):
		return self

	def __exit__(self, *args, **kwargs):
		self.close()

	def SendAndRecieve(self, cmd):
		self.logger.debug("Sending '%s'", cmd)
		self.io.write(cmd + '\r\n')
		self.ser.flush()

		# Receive an answer:
		res = self.io.readline()
		res = res.strip()
		if res == 'Syntax Error':
			self.logger.error("Syntax Error: '%s'", cmd)
			return None
		self.logger.debug("Received '%s'" % res)
		if res == '':
			return None
		elif cmd == '*': # Special case for "TIME"
			return res[5:]
		elif res.startswith(cmd + ','):
			return res[len(cmd)+1:]
		else:
			return res

	@property
	def position(self):
		"""Current position."""
		return self.SendAndRecieve('POSITION')

	@property
	def time(self):
		"""Current UTC time."""
		ts = self.SendAndRecieve('*')
		return datetime.strptime(ts[3:-2], '%Y,%j,%H,%M,%S.%f')

	@property
	def version(self):
		"""Version of GPC Clock."""
		return self.SendAndRecieve('VERSION')

	@property
	def faults(self):
		"""List of current faults."""
		flts = self.SendAndRecieve('FLTS')
		flts = int(flts)
		if flts == 0:
			return None
		# There was an error, figure out which ones:
		faults = []
		for bitval, description in self.FAULTS.items():
			if flts & bitval > 0:
				faults.append(description)
		return faults

	def setPulseTime(self):
		self.SendAndRecieve('PPTIME,XXX:XX:XX:X0.0000000')
		self.SendAndRecieve('PPMODE,1')
		self.SendAndRecieve('PPTIME')

if __name__ == '__main__':

	print("starting")
	with GPSClock('COM5') as c:
		print(c.version)
		print(c.time)
		print(c.position)
		print(c.faults)

		c.setPulseTime()