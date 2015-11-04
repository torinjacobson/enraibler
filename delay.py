#!/usr/bin/python

import pygst
pygst.require("0.10")
import gst
import pygtk
import gtk
import sys

# Audio delay code thanks to d53richar on Ubuntu Forums.
# http://ubuntuforums.org/showthread.php?t=1189559

class Main:
	def __init__(self):
		DELAY = float(sys.argv[1])
		DELAY = long(DELAY * 1000000000)
		print DELAY
		
		## ALSA
		self.delay_pipeline = gst.Pipeline("mypipeline")
		self.audiosrc = gst.element_factory_make("jackaudiosrc", "audio")
		self.delay_pipeline.add(self.audiosrc)
		
		## Queue
		self.audioqueue = gst.element_factory_make("queue", "queue1")
		self.audioqueue.set_property("max-size-time", 0)
		self.audioqueue.set_property("max-size-buffers", 0)
		self.audioqueue.set_property("max-size-bytes", 0)
		self.audioqueue.set_property("min-threshold-time", DELAY)
		self.audioqueue.set_property("leaky", "no")
		
		self.delay_pipeline.add(self.audioqueue)

		## Audio Output
		self.sink = gst.element_factory_make("autoaudiosink", "sink")
		self.delay_pipeline.add(self.sink)

		## Link the elements
		self.audiosrc.link(self.audioqueue)
		self.audioqueue.link(self.sink)

		## Begin Playback
		self.delay_pipeline.set_state(gst.STATE_PLAYING)

start = Main()
gtk.main()

