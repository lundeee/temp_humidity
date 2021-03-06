#!/usr/bin/python

# Written by David Neuy
# Version 0.1.0 @ 03.12.2014
# This script was first published at: http://www.home-automation-community.com/
# You may republish it as is or publish a modified version only when you 
# provide a link to 'http://www.home-automation-community.com/'. 

#install dependency with 'sudo easy_install apscheduler' NOT with 'sudo pip install apscheduler'
import os, sys, Adafruit_DHT, time
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler

sensor                       = Adafruit_DHT.AM2302 #DHT11/DHT22/AM2302
pin                          = 2
sensor_name                  = "studio_grad"
values_path                  = "/var/www/html/"
# hist_temperature_file_path   = values_path+"sensor-values/temperature_" + sensor_name + "_log_" + str(date.today().year) + ".csv"
# latest_temperature_file_path = values_path+"sensor-values/temperature_" + sensor_name + "_latest_value.csv"
# hist_humidity_file_path      = values_path+"sensor-values/humidity_" + sensor_name + "_log_" + str(date.today().year) + ".csv"
# latest_humidity_file_path    = values_path+"sensor-values/humidity_" + sensor_name + "_latest_value.csv"

hist_temperature_file_path   = values_path+"sensor-values/temperature_log.csv" 
latest_temperature_file_path = values_path+"sensor-values/temperature_latest.txt"
hist_humidity_file_path      = values_path+"sensor-values/humidity_log.csv"
latest_humidity_file_path    = values_path+"sensor-values/humidity_latest.txt"

csv_header_temperature       = "timestamp,temperature_in_celsius\n"
csv_header_humidity          = "timestamp,relative_humidity\n"
csv_entry_format             = "{:%Y-%m-%d %H:%M:%S},{:0.1f}\n"
sec_between_log_entries      = 60
latest_humidity              = 0.0
latest_temperature           = 0.0
latest_value_datetime        = None

def write_header(file_handle, csv_header):
  file_handle.write(csv_header)

def write_value(file_handle, datetime, value):
  line = csv_entry_format.format(datetime, value)
  #print(file_handle)
  file_handle.write(line)
  file_handle.flush()

def open_file_ensure_header(file_path, mode, csv_header):
  f = open(file_path, mode, os.O_NONBLOCK)
  if os.path.getsize(file_path) <= 0 and csv_header != "":
    write_header(f, csv_header)
  return f

def write_hist_value(): 
  write_value(f_hist_temp, latest_value_datetime, latest_temperature)
  write_value(f_hist_hum, latest_value_datetime, latest_humidity)

def write_latest_value():
    with open_file_ensure_header(latest_temperature_file_path, 'w',"") as f_latest_value:  #open and truncate
        f_latest_value.write( "Temperature: " +'%.1f' % latest_temperature + "\nHumidity: %.1f" % latest_humidity)

f_hist_temp = open_file_ensure_header(hist_temperature_file_path, 'a', csv_header_temperature)
f_hist_hum  = open_file_ensure_header(hist_humidity_file_path, 'a', csv_header_humidity)

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
#import pylcdlib
#lcd = pylcdlib.lcd(0x27,1,1)

#lcd.lcd_puts("Initializing.." ,1) 
#lcd.lcd_puts("  s  " ,2) 


print "Ignoring first 2 sensor values to improve quality..."
for x in range(2):
  Adafruit_DHT.read_retry(sensor, pin)


print "Creating interval timer. This step takes almost 2 minutes on the Raspberry Pi..."
#create timer that is called every n seconds, without accumulating delays as when using sleep
scheduler = BackgroundScheduler()
scheduler.add_job(write_hist_value, 'interval', seconds=sec_between_log_entries)
scheduler.start()
print "Started interval timer which will be called the first time in {0} seconds.".format(sec_between_log_entries);

try:
  while True:
    hum, temp = Adafruit_DHT.read_retry(sensor, pin)
    if hum is not None and temp is not None:
      latest_humidity, latest_temperature = hum, temp
      latest_value_datetime = datetime.today()
      write_latest_value()
      write_hist_value()
      #print(str(latest_humidity)+"% "+str(latest_temperature)+"C")
    time.sleep(1)
except (KeyboardInterrupt, SystemExit):
  scheduler.shutdown()

