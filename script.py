# 20160424 - Smart Printer v0.1

# Imports
import os
import ftplib
import re
import time
import urllib2
import sane
from PIL import Image
from urllib2 import urlopen
from cookielib import CookieJar
from urllib import urlretrieve

# Uique key for each process
timeId = str(int(time.time()));

# Get image from scanner
depth = 8
mode = 'color'

ver = sane.init()
print("init()");
devices = sane.get_devices()
print('Available devices:', devices)
dev = sane.open(devices[0][0])
print("openDevices()");
params = dev.get_parameters()
print("get_params()");

try:
    dev.resolution = 72
except:
    print('Cannot set resolution, defaulting to %d' % params[1])    

try:
    dev.mode = mode
except:
    print('Cannot set mode, defaulting to %s' % params[0])

try:
    dev.br_x = 208.
    dev.br_y = 292.
except:
    print('Cannot set scan area, using default')

filename = "input-"+timeId+".png"

dev.start()
im = dev.snap()
im.save(filename)


# Send it to server

session = ftplib.FTP('domain.host.extension','user','pass')
file = open(filename,'rb')
session.cwd('/www/smart-printer/inputs')
session.storbinary('STOR '+filename, file)
file.close()
session.quit()

fileurl = "http://ssl15.ovh.net/~fclmprod/mart-printer/inputs/"+filename;

# Reverse image lookup
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')]

googlepath = 'https://www.google.com/searchbyimage?&image_url='+fileurl

sourceCode = opener.open(googlepath).read()
findLinks = re.findall(r'<div class="rg_meta">{"id":".*?,"oh":.*?,"ou":"(.*?)","ow":.*?',sourceCode)

# Download file
urlretrieve(findLinks[0], "output-"+timeId+".png")

# Convert to .bmp
file_in = "output-"+timeId+".png"
img = Image.open(file_in)
file_out = "output-"+timeId+".bmp"
img.save(file_out)

# Print from command line
fn = file_out ## Will not print if > than A4
printer = 'HP_Deskjet_3520_series'
print_cmd = 'lpr -P %s %s'
os.system(print_cmd % (printer, fn))
print('printed !')
