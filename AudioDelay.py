#!/usr/bin/python

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
import sys
import time

GObject.threads_init()
Gst.init(None)
# Audio delay code thanks to d53richar on Ubuntu Forums.
# http://ubuntuforums.org/showthread.php?t=1189559

class AudioDelay():
    def __init__(self):

        self.pipeline = Gst.Pipeline()

        ## Jack Audio
        self.audiosrc = Gst.ElementFactory.make("jackaudiosrc", "audio")
        self.pipeline.add(self.audiosrc)
        
        ## Queue
        self.audioqueue = Gst.ElementFactory.make("queue", "queue1")
        self.audioqueue.set_property("max-size-time", 0)
        self.audioqueue.set_property("max-size-buffers", 0)
        self.audioqueue.set_property("max-size-bytes", 0)
        self.audioqueue.set_property("leaky", 0)
        self.pipeline.add(self.audioqueue)
        
        ## Volume
        self.volume = Gst.ElementFactory.make("volume", "volume")
        self.pipeline.add(self.volume)

        ## Audio Output
        self.sink = Gst.ElementFactory.make("jackaudiosink", "sink")
        self.pipeline.add(self.sink)

        #self.fakesink = Gst.ElementFactory.make("fakesink", "sink2")
        #self.pipeline.add(self.fakesink)

        ## Link the elements
        self.audiosrc.link(self.audioqueue)
        self.audioqueue.link(self.volume)
        self.volume.link(self.sink)
        
        self.audioqueue.set_property("min-threshold-time", long(1 * Gst.MSECOND))

    def begin_delay_ms(self, delay_ms):
        self.pipeline.set_state(Gst.State.PAUSED)
        self.audioqueue.set_property("min-threshold-time", long(delay_ms * Gst.MSECOND))
#        self.fakesink.set_render_delay(long(delay_ms*Gst.MSECOND))
        self.pipeline.set_state(Gst.State.PLAYING)

    def kill(self):
        self.pipeline.set_state(Gst.State.NULL)

    def setvolume(self, volume):
        self.volume.set_property('volume', volume)

    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())
