#KextManager, a lightweight and commandline alternative to multibeast.
#Created by /u/GotKrypto76.
#Big thanks to /u/CorpNewt, check out his github account for other awesome tools! (https://github.com/corpnewt)
#This is probably unsafe to run on genuine Mac computers.

#Imports
from subprocess import Popen, PIPE
import urllib2
import json
import glob
import sys
import imp
import os

#Globals
DEBUG = True
kextArray = []
kextDirs = ['/Library/Extensions',
            '/System/Library/Extensions',
            '/EFI/CLOVER/kexts/*',
            '/EFI/CLOVER/kexts/Other',
            '/Volumes/EFI/EFI/CLOVER/kexts/*',
            '/Volumes/EFI/EFI/CLOVER/kexts/Other',
            '/Extra/Extensions']
kextSite = {"Name": "Virulent Kext Directory",
            "URLs": {
            		"API": "http://virulent.pw/KextDirectory/api.php",
            		"Status": "http://virulent.pw/KextDirectory/status.php",
            		"Home": "http://virulent.pw"
            		},
            "Reachable": 0, # Where 0 = unknown, 1 = no, 2 = yes. Leave this 0, its programmatically changed.
            "TotalKexts": 0, # Leave this alone, its programmatically changed.
			"Args": { 
				"API": {
					"Action": "A",
					"KextName": "N",
					"KextVersion": "V",
					"Client": "C"
				},
				"Status": {
					"Client": "C"
				}
			}
		}
#Funcs
def prettyprint(type, message):
    if type == 0:
        if DEBUG:
            print("\033[94m[DEBUG] %s\033[0m" % (message))
    elif type == 1:
        print("\033[92m[INFO] %s\033[0m" % (message))
    elif type == 2:
        print("\033[93m[WARNING] %s\033[0m" % (message))
    elif type == 3:
        print("\033[91m[ERROR] %s\033[0m" % (message))
    else:
        print message

#http://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
def confirm(default='no'):
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = raw_input("> ")
    values = ('y', 'yes', '') if choices == 'Y/n' else ('y', 'yes')
    one = choice.strip().lower() == "y"
    two = choice.strip().lower() == "n"
    three = choice.strip().lower() == "yes"
    four = choice.strip().lower() == "no"
    if (one or two or three or four):
        return choice.strip().lower() in values
    else:
    	prettyprint(3, "Please enter 'Yes' or 'No'.")
        warn_confirm()

def genuine_warning():
	print "===============WARNING==============="
	print "| It appears that you are trying to |"
	print "| run this on a regular genuine Mac |"
	print "| . This script is only meant to be |"
	print "| ran on Hackintoshes, and may do   |"
	print "| damage to genuine Mac computers.  |"
	print "====================================="
	print "| Type 'Yes' to continue the script |"
	print "| Type 'No' to exit the script      |"
	print "====================================="
	if confirm() is False:
		sys.exit(0)


def is_hackintosh():
    if len(os.popen("kextstat | grep FakeSMC").read()) >= 5:
        return True
    else:
        return False

#http://stackoverflow.com/questions/12886768/how-to-unzip-file-in-python-on-all-oses
def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                while True:
                    drive, word = os.path.splitdrive(word)
                    head, word = os.path.split(word)
                    if not drive:
                        break
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            zf.extract(member, path)

#Intro
prettyprint(1, "Welcome to KextManager.")
prettyprint(1, "Brought to you by:")
prettyprint(1, "/u/GotKrypto and /u/CorpNewt")

#Create working directory
if os.path.exists('./KextManager') is False:
    prettyprint(1, "Creating working directory..")
    os.mkdir('./KextManager');
if os.path.exists('./KextManager/Bins') is False:
    prettyprint(1, "Creating 'KextManager/Bins")
    os.mkdir('./KextManager/Bins')
if os.path.exists('./KextManager/Downloads') is False:
    prettyprint(1, "Creating 'KextManager/Downloads")
    os.mkdir('./KextManager/Downloads')
if os.path.exists('./KextManager/Bins/MountEFI') is False:
	prettyprint(1, "Downloading MountEFI to 'KextManager/Bins/MountEFI")
	file = urllib2.urlopen("https://raw.githubusercontent.com/corpnewt/Bash-Scripts/master/MountEFI")
	with open('./KextManager/Bins/MountEFI','wb') as output:
	  output.write(file.read())
	prettyprint(1, "Giving MountEFI executable permissions.")
	os.popen('chmod +x ./KextManager/Bins/MountEFI')
if os.path.exists('./KextManager/Bins/RepairAndRebuild') is False:
	prettyprint(1, "Downloading RepairAndRebuild to 'KextManager/Bins/RepairAndRebuild")
	file = urllib2.urlopen("https://raw.githubusercontent.com/corpnewt/Bash-Scripts/master/Repair%20and%20Rebuild")
	with open('./KextManager/Bins/RepairAndRebuild','wb') as output:
	  output.write(file.read())
	prettyprint(1, "Giving RepairAndRebuild executable permissions.")
	os.popen('chmod +x ./KextManager/Bins/RepairAndRebuild')

#Warning
if is_hackintosh() is False:
    prettyprint(0, "User is not running on a hackintosh.")
    genuine_warning()
    prettyprint(0, "User has opted to continue anyway.")
else:
    prettyprint(0, "User is running on a hackintosh, will not display warning.")

#Check for plistlib
##In all reality, this shouldn't be a problem, but it can't hurt to check.
try:
    imp.find_module('plistlib')
    import plistlib
except ImportError:
	prettyprint(3, "It appears you don't have plistlib installed.\nWe need that to parse kext info.")
	sys.exit(1)

#Mount EFI partitions if any.
prettyprint (1, "Do you have an EFI partition to mount?")
prettyprint(1, "Please enter 'Yes' or 'No'")
if confirm():
	print Popen(["./KextManager/Bins/MountEFI"]).communicate()[0]

#Search for all kexts.
prettyprint(1, ("Will search for kext files in %i directories.." % (len(kextDirs))))
for dir in kextDirs:
	prettyprint(1, ("Searching '%s'.." % (dir)))
	globResult = glob.glob(dir+'/*.kext')
	prettyprint(0, ("Total items in result: %i" % (len(globResult))))
	if len(globResult) > 0:
	    kextArray.append(globResult)
	prettyprint(1, ("Found %i kexts." % (len(globResult))))

#Start connecting to kext database website specified up in globals.
##Check connection
prettyprint(1, ("Checking connection to %s.." % (kextSite['Name'])))
try:
    callURL = kextSite['URLs']['Status']+"?"+kextSite['Args']['Status']['Client']+"=KextManager"
    prettyprint(0, ("Calling URL: %s" % (callURL)))
    if urllib2.urlopen(callURL).read() == "OK":
        prettyprint(1, "Connection established!")
    else:
        prettyprint(3, "Failed. Quitting..")
        sys.exit(1)
except Exception:
    prettyprint(3, "Failed. Quitting..")
    sys.exit(1)

##Get total kexts
prettyprint(1, ("Getting kext count at %s.." % (kextSite['Name'])))
try:
    callURL = kextSite['URLs']['API']+"?"+kextSite['Args']['API']['Client']+"=KextManager&"+kextSite['Args']['API']['Action']+"=getTotalKexts"
    prettyprint(0, ("Calling URL: %s" % (callURL)))
    kextSite['TotalKexts'] = json.loads(urllib2.urlopen(callURL).read())['TotalKexts']
    prettyprint(1, ("%s has %i kexts available." % (kextSite['Name'], kextSite['TotalKexts'])))
except Exception:
    prettyprint(3, "Failed. Quitting..")
    sys.exit(1)

