#!/usr/bin/python3
#------------------------------------------------------------------------------
# sense.py: CLI tool for extracting data from the Sense hat
#------------------------------------------------------------------------------
# (c) 2018 - J R Whitehead (richard@whitehead.com)
#------------------------------------------------------------------------------

import sys
import os
import time
import datetime
from sense_hat import SenseHat

TEMP_OFFSET = 5
OUTLIER_THRESHOLD = 2
retry = 15

a = sys.argv[1]

sense = SenseHat()
sense.clear()

def recordTemp(temp):
    with open('/tmp/lastTemp.txt','r+') as f:
        ots = f.read()
        ot = float( ots.replace("\n","") )
        if ot < temp:
            if temp - ot > OUTLIER_THRESHOLD:
                val = ot
            else:
                val = temp
        elif ot >= temp:
            if ot - temp > OUTLIER_THRESHOLD:
                val = ot
            else:
                val = temp
        with open('/tmp/lastTemp.txt','w+') as f:
            f.write(str(val))
    f.closed

def log(name,retry,r):
    with open('/tmp/rtcnt.txt','a') as f:
        f.write(curTime()+' '+str(name)+'('+str(retry)+'): '+str(r)+'\n')
    f.closed

def curTime():
    now = datetime.datetime.now()
    c = ':'
    time_now = str(now.day) +' '+ str(now.hour) +c+ str(now.minute) +c+ str(now.second)
    return(time_now)

def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    t = float(res.replace("temp=","").replace("'C\n",""))
    return(t)

def get_data(func,name,upper,lower):
    "Wrap the sense get methods with some validation and retry"
    global retry
    while retry > 0:
        r = func
        if r == 0 or r > upper or r < lower:
            retry -= 1
            time.sleep( 1 )
        else:
            return(r)
    sys.exit(3)

if a == 'temp':
    ht = get_data(sense.get_temperature_from_pressure(),a,50,10)
    if ht > 0:
        t = ht - (( get_cpu_temp()-ht )/TEMP_OFFSET )
        m = round(1.8*t + 23 , 1)
        recordTemp(m)
    else:
        m = 0

elif a == 'press':
    m = get_data(sense.get_pressure(),a,1200,950)

elif a == 'humid':
    m = get_data(sense.get_humidity(),a,50,5)

elif a == 'comp':
    m = get_data(sense.get_compass(),a,361,1)

else:
    print("Usage: sense <comp|temp|humid|press>")
    sys.exit(2)

if m != 0:
    print( round(m, 1) )
    sys.exit(0)
else:
    sys.exit(1)
