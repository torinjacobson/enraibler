#!/usr/bin/env python

import os
if (os.geteuid() != 0):
	exit("Must run as root!")
import pty
import subprocess
import time



class JackdInit:
	jackd_command = '/usr/local/bin/jackd -R -P10 -T -dalsa -r48000 -S -p256 -n2 -D -Chw:sndrpiproto,0 -Phw:sndrpiproto,0'

	def __init__(self):
		# Start jackd if it's not already running
		try:
			pid = int(subprocess.check_output("pgrep jackd", shell=True))
		except (ValueError):
			pid = 0

		if (pid):
			print "jackd pid = " + str(pid)
		else:
			master, slave = pty.openpty()
			p = subprocess.Popen(self.jackd_command.split(), stdin=subprocess.PIPE, stdout=slave, stderr=slave, close_fds=True)
			stdout = os.fdopen(master)
			print "Starting jackd..."
			out = ""
			# Wait for jackd to finish initialization
			while "final selected sample format for playback" not in out:
				out = stdout.readline()
				# print out
			# Add a little delay after jackd init to be safe
			time.sleep(0.1)
			print "done"
