import sys
import os
import xbmc
import string

__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/scripts/xbTweet/"
__version__ = "0.0.891"

#Path handling
LANGUAGE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'language' ) )
CONFIG_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'settings.cfg' ) )
AUTOEXEC_PATH = xbmc.translatePath( 'special://home/scripts/autoexec.py' )
VERSION_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'version.cfg' ) )

#Consts
AUTOEXEC_SCRIPT = 'import time;time.sleep(5);xbmc.executebuiltin("XBMC.RunScript(special://home/scripts/xbtweet/default.py,-startup)")' 

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString
__settings__ = xbmc.Settings( path=os.getcwd() )

def Debug(message, Verbose=True):
    bVerbose = __settings__.getSetting( "debug" )
    if (bVerbose == 'true'):
        bVerbose = True
    else:
        bVerbose = False
    
    if (bVerbose and Verbose):
        print message
    elif (not Verbose):
        print message

def CheckVersion():
    Version = ""
    if (os.path.exists(VERSION_PATH)):
        versionfile = file(VERSION_PATH, 'r')
        Version = versionfile.read()        
    return Version

def WriteVersion(Version):
    print Version
    print VERSION_PATH
    versionfile = file(VERSION_PATH, 'w')
    versionfile.write (Version)
    versionfile.close()

def CheckIfFirstRun():
    global CONFIG_PATH
    if (os.path.exists(CONFIG_PATH)):
        return False
    else:
        return True
    
def CheckIfUpgrade():
    return False

def CalcPercentageRemaining(currenttime, duration):
    iCurrentMinutes = (int(currenttime.split(':')[0]) * 60) + int(currenttime.split(':')[1])
    iDurationMinutes = (int(duration.split(':')[0]) * 60) + int(duration.split(':')[1])
    return float(iCurrentMinutes) / float(iDurationMinutes) 

def SetAutoStart(bState = True):
    Debug( '::AutoStart::' + str(bState), True)
    if (os.path.exists(AUTOEXEC_PATH)):
        Debug( 'Found Autoexec.py file, checking we''re there', True)
        bFound = False
        autoexecfile = file(AUTOEXEC_PATH, 'r')
        filecontents = autoexecfile.read()
        lines_fixed = ""
        autoexecfile.seek(0)
        while 1:
            lines = autoexecfile.readlines(1000)
            if not lines: break
            for line in lines:
                if (string.find(line, 'xbtweet') > 1):
                    Debug( 'Found our script, no need to do anything', True)
                    bFound = True
                else:
                    lines_fixed = lines_fixed + line + '\r\n'
        autoexecfile.close()
        if (not bFound):
            Debug( 'Appending our script to the autoexec.py script', True)
            autoexecfile = file(AUTOEXEC_PATH, 'w')
            autoexecfile.write (filecontents + '\r\n' + AUTOEXEC_SCRIPT)
            autoexecfile.close()
        if (bFound and not bState):
            #remove line
            Debug( 'Removing our script from the autoexec.py script', True)
            autoexecfile = file(AUTOEXEC_PATH, 'w')
            autoexecfile.write (lines_fixed)
            autoexecfile.close()            
    else:
        Debug( 'File Autoexec.py is missing, creating file with autostart script', True)
        autoexecfile = file(AUTOEXEC_PATH, 'w')
        autoexecfile.write (AUTOEXEC_SCRIPT)
        autoexecfile.close()
    Debug( '::AutoStart::'  , True)

#Check for new version
if __settings__.getSetting( "new_ver" ) == "true":
    try:
        import re
        import urllib
        if not xbmc.getCondVisibility('Player.Paused') : xbmc.Player().pause() #Pause if not paused	
        usock = urllib.urlopen(__svn_url__ + "default.py")
        htmlSource = usock.read()
        usock.close()

        version = re.search( "__version__.*?[\"'](.*?)[\"']",  htmlSource, re.IGNORECASE ).group(1)
        Debug ( "SVN Latest Version :[ "+version+"]", True)
        
        if version > __version__:
            import xbmcgui
            dialog = xbmcgui.Dialog()
            selected = dialog.ok(__language__(30002) % (str(__version__)),__language__(30003) % (str(version)),__language__(30004))
    except:
        print 'Exception in reading SVN'
