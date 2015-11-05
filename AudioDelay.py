#!/usr/bin/python

import pygst
pygst.require("0.10")
import gst
import sys
import time

# Audio delay code thanks to d53richar on Ubuntu Forums.
# http://ubuntuforums.org/showthread.php?t=1189559

class AudioDelay:
	def __init__(self):
		## ALSA
		self.delay_pipeline = gst.Pipeline("mypipeline")
		self.audiosrc = gst.element_factory_make("jackaudiosrc", "audio")
		self.delay_pipeline.add(self.audiosrc)
		
		## Queue
		self.audioqueue = gst.element_factory_make("queue", "queue1")
		self.audioqueue.set_property("max-size-time", 0)
		self.audioqueue.set_property("max-size-buffers", 0)
		self.audioqueue.set_property("max-size-bytes", 0)
		self.audioqueue.set_property("leaky", "no")
		
		self.delay_pipeline.add(self.audioqueue)

		## Audio Output
		self.sink = gst.element_factory_make("autoaudiosink", "sink")
		self.delay_pipeline.add(self.sink)

		## Link the elements
		self.audiosrc.link(self.audioqueue)
		self.audioqueue.link(self.sink)

	def begin_delay_ms(self, delay_ms):
		delay_ns = long( float(delay_ms) * 1000000 )
		self.delay_pipeline.set_state(gst.STATE_PAUSED)
		self.audioqueue.set_property("min-threshold-time", delay_ns)
		self.delay_pipeline.set_state(gst.STATE_PLAYING)

	def kill(self):
		self.delay_pipeline.set_state(gst.STATE_NULL)
