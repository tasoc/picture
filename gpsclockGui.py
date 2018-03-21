#!/usr/bin/python
# gpsFlasher
# Gui to configure a gps based Flash light
# by Eric Weiss ew@phys.au.dk
#    Rasmus Handberg rasmush@phys.au.dk
#
# With this gui you cat set up da date  when and how long the LED lamp should flash
# the Values are written to config.ini on apply.
# and read on startup.
# on raspberry pi you can use IO pins to stretch the Pulse pin with the puse setting.
#
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import ConfigParser

import io
import serial
import argparse

import time



ConfigFile='config.ini'
class gpsFlasher(Gtk.Window):

    def __init__(self,conf):
        self.config=conf
        (Year,Month,Day)=self.config.get("settings",'date').split('/')
        (Hour,Minute,Sec)=self.config.get("settings",'time').split(':')
        flashpulse=float(self.config.get("settings",'pulse'))
        
        self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, parity=serial.PARITY_NONE, timeout=1.0)
        self.io = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser, 1),
                       newline = '\n',
                       line_buffering = True)

        # Make sure we are using the right settings:
        self.SendAndRecieve('ECHO,0') # Turn echoing of commands off
        self.SendAndRecieve('TMODE,0') # 0=UTC, 1=GPS, 2=LOCAL
        self.SendAndRecieve('DSTSTATE,0') # Disable Daylight Savings Time
        self.SendAndRecieve('PPMODE,0') # Disable Programmable Pulse
        

        Gtk.Window.__init__(self, title="GpsFlasher")
        self.set_border_width(10)
        grid = Gtk.Grid()
        self.add(grid)
        self.Mainlabel = Gtk.Label("gpsFlasher")
        self.Datelabel = Gtk.Label("Date")
        self.Timelabel = Gtk.Label("Time")
        self.Pulselabel = Gtk.Label("PulseLenght")
        self.Yearlabel = Gtk.Label("Year")
        self.Monthlabel = Gtk.Label("Month")
        self.Daylabel = Gtk.Label("Day")
        self.Hourlabel = Gtk.Label("Hour")
        self.Minutelabel = Gtk.Label("Minute")
        self.Seclabel = Gtk.Label("Seconds")

        self.adjustYear= Gtk.Adjustment(value=float(Year), lower=2018, upper=2027, step_incr=1, page_incr=5, page_size=0)
        self.adjustMonth= Gtk.Adjustment(value=float(Month), lower=0, upper=12, step_incr=1, page_incr=.4, page_size=0)
        self.adjustDay= Gtk.Adjustment(value=float(Day), lower=1, upper=31, step_incr=1, page_incr=.5, page_size=0)
        self.adjustHour= Gtk.Adjustment(value=float(Hour), lower=00, upper=23, step_incr=1, page_incr=1, page_size=0)
        self.adjustMinute= Gtk.Adjustment(value=float(Minute), lower=00, upper=59, step_incr=1, page_incr=1, page_size=0)
        self.adjustSec= Gtk.Adjustment(value=float(Sec), lower=0, upper=59, step_incr=1, page_incr=1, page_size=0)
        self.adjustSpPulse= Gtk.Adjustment(value=flashpulse, lower=.01, upper=.99, step_incr=.01, page_incr=.1, page_size=0)

        self.button = Gtk.Button.new_with_mnemonic("_Close")
        self.Applybutton = Gtk.Button.new_with_mnemonic("Apply")
       
        self.spin_button_Year = Gtk.SpinButton(adjustment=self.adjustYear, climb_rate=1, digits=0)
        self.spin_button_Month = Gtk.SpinButton(adjustment=self.adjustMonth, climb_rate=1, digits=0)
        self.spin_button_Day = Gtk.SpinButton(adjustment=self.adjustDay, climb_rate=1, digits=0)
        self.spin_button_Hour = Gtk.SpinButton(adjustment=self.adjustHour, climb_rate=1, digits=0)
        self.spin_button_Minute = Gtk.SpinButton(adjustment=self.adjustMinute, climb_rate=1, digits=0)
        self.spin_button_Sec = Gtk.SpinButton(adjustment=self.adjustSec, climb_rate=1, digits=0)
        self.spin_button = Gtk.SpinButton(adjustment=self.adjustSpPulse, climb_rate=.01, digits=2)
        grid.attach(self.Mainlabel,0,0,2,1)
        grid.attach_next_to(self.Datelabel,self.Mainlabel,Gtk.PositionType.BOTTOM, 1, 3)
        grid.attach_next_to(self.Timelabel,self.Datelabel,Gtk.PositionType.BOTTOM, 1, 3)
        grid.attach_next_to(self.Pulselabel,self.Timelabel,Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.spin_button_Year,self.Datelabel,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.Yearlabel,self.spin_button_Year,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.spin_button_Month,self.spin_button_Year,Gtk.PositionType.BOTTOM, 1 ,1)
        grid.attach_next_to(self.Monthlabel,self.spin_button_Month,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.spin_button_Day,self.spin_button_Month,Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.Daylabel,self.spin_button_Day,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.spin_button_Hour,self.Timelabel,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.Hourlabel,self.spin_button_Hour,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.spin_button_Minute,self.spin_button_Hour,Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.Minutelabel,self.spin_button_Minute,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.spin_button_Sec,self.spin_button_Minute,Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(self.Seclabel,self.spin_button_Sec,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.spin_button,self.Pulselabel,Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.Applybutton,self.Pulselabel,Gtk.PositionType.BOTTOM, 3, 1)
        grid.attach_next_to(self.button,self.Applybutton,Gtk.PositionType.BOTTOM, 3, 1)
        self.button.connect("clicked", self.on_close_clicked)
        self.Applybutton.connect("clicked", self.on_Apply_clicked)
#        self.adjustYear.connect("value_changed", self.Year_toggled)
#        self.adjustMonth.connect("value_changed", self.Month_toggled)
#        self.adjustDay.connect("value_changed", self.Day_toggled)
#        self.adjustHour.connect("value_changed", self.Hour_toggled)
#        self.adjustMinute.connect("value_changed", self.Minute_toggled)
#        self.adjustSec.connect("value_changed", self.Sec_toggled)
#        self.adjustSpPulse.connect("value_changed", self.Pulse_toggled)
        
#    def Year_toggled(self,spinner):
#        print ("Year Toggled")
#    def Month_toggled(self,spinner):
#        print ("Year Toggled")
#    def Day_toggled(self,spinner):
#        print ("Year Toggled")
#    def Hour_toggled(self,spinner):
#        print ("Year Toggled")
#    def Minute_toggled(self,spinner):
#        print ("Year Toggled")
#    def Sec_toggled(self,spinner):
#        print ("Year Toggled")
#    def Pulse_toggled(self,spinner):
#        pass
    def SendAndRecieve(self, cmd):
#        self.logger.debug("Sending '%s'", cmd)
        self.io.write(unicode(cmd, "utf-8") + '\r\n')
        self.ser.flush()

        # Receive an answer:
        res = self.io.readline()
        res = res.strip()
        if res == 'Syntax Error':
#            self.logger.error("Syntax Error: '%s'", cmd)
            return None
 #       self.logger.debug("Received '%s'" % res)
        if res == '':
            return None
        elif cmd == '*': # Special case for "TIME"
            return res[5:]
        elif res.startswith(cmd + ','):
            return res[len(cmd)+1:]
        else:
            return res
        
    def on_open_clicked(self, button):
        print("\"Open\" button was clicked")
        
    def on_Apply_clicked(self, button):
#        print("\"Apply\" button was clicked")
        self.config.set("settings",'pulse',self.adjustSpPulse.get_value())
        StrHour= "%i" % self.adjustHour.get_value()
        StrMinute= "%i" % self.adjustMinute.get_value()
        StrSec= "%i" % self.adjustSec.get_value()
        StrYear= "%i" % self.adjustYear.get_value()
        StrMonth= "%i" % self.adjustMonth.get_value()
        StrDay= "%i" % self.adjustDay.get_value()
        self.config.set("settings",'date',"%s/%s/%s" % (StrYear,StrMonth,StrDay))
        self.config.set("settings",'time',"%s:%s:%s" % (StrHour,StrMinute,StrSec))
        self.config.set("settings",'pulse',self.adjustSpPulse.get_value())
        with open(ConfigFile, 'wb') as configfile:
            self.config.write(configfile)
            configfile.close()
        import datetime
        a=datetime.datetime(int(StrYear), int(StrMonth), int(StrDay), hour=int(StrHour), minute=int(StrMinute), second=int(StrSec), microsecond=0, tzinfo=None)
        sendStr="PPTIME,%03i:%02i:%02i:%02i.0000000" % (a.timetuple().tm_yday, a.timetuple().tm_hour,a.timetuple().tm_min,a.timetuple().tm_sec )
        self.SendAndRecieve(sendStr)
        self.SendAndRecieve('PPMODE,1')

        
    def on_close_clicked(self, button):
 #       print("Closing application")
        Gtk.main_quit()


def buttonEventHandler (pin):
 #   print "handling button event"

    # turn the green LED on
 #   GPIO.output(25,True)

    time.sleep(1)

    # turn the green LED off
 #   GPIO.output(25,False)
    
def main():
    with open(ConfigFile) as f:
        sample_config = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(sample_config))
#    GPIO.setmode(GPIO.BCM)
#    GPIO.setup(23,GPIO.IN)
#    GPIO.setup(24,GPIO.OUT)
#    GPIO.setup(25,GPIO.OUT)
#    GPIO.add_event_detect(23,GPIO.FALLING)
#    GPIO.add_event_callback(23,buttonEventHandler,100)
    win = gpsFlasher(config)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
#    GPIO.cleanup()
    
    return 0
  	
if __name__ == "__main__":
    main()
