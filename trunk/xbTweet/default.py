import sys
import os
import xbmc
import xbmcgui
import string
import webbrowser
import time
import ConfigParser
import string

__scriptname__ = "xbTweet"
__author__ = "Itay Weinberger"
__url__ = "http://www.xbmcblog.com"
__svn_url__ = "http://xbtweet.googlecode.com/svn/trunk/xbTweet/"
__credits__ = ""
__version__ = "0.0.422"
__XBMC_Revision__ = ""


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
            
def CheckIfFirstRun():
    if (os.path.exists(CONFIG_PATH)):
        return False
    else:
        return True
    
def CheckIfUpgrade():
    return False

def CreateAPIObject():
    Debug( '::CreateAPIObject::' , True)
    if (bOAuth):
        Debug( 'Using OAuth', True)
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_PATH)

        if (config.has_section('Twitter Account')):
            twitter_key = config.get('Twitter Account', 'key')
            twitter_secret = config.get('Twitter Account', 'secret')

            auth = OAuthHandler('OAWDRnhOHMLpLgEaoWFNA', '8Ros5aIic3L5uoASMZ1JxyNyGlS9xM1Gh0jsReWDws')
            auth.set_access_token(twitter_key, twitter_secret)
            api = API(auth)
        
            api.retry_count = 2
            api.retry_delay = 5
            
            bTwitterAccountDetailsSet = True
            return api
        else:
            return False
    else:
        Debug( 'Using Plain Authentication, ' + username + ':' + password, True)
        auth = BasicAuthHandler(username, password)
        api = API(auth)
    
        api.retry_count = 2
        api.retry_delay = 5
        
        bTwitterAccountDetailsSet = True
        return api
    
    Debug( '::CreateAPIObject::', True)

def StartOAuthProcess():
    Debug( '::StartOAuthProcess::', True)
    auth = OAuthHandler('OAWDRnhOHMLpLgEaoWFNA', '8Ros5aIic3L5uoASMZ1JxyNyGlS9xM1Gh0jsReWDws')
    redirect_url = auth.get_authorization_url()
    webbrowser.open(redirect_url)
    keyboard = xbmc.Keyboard('','Enter Twitter PIN Code')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        password = keyboard.getText()
    else:
        return False          

    try:
        token = auth.get_access_token(password)
        twitter_key = token.key
        twitter_secret = token.secret
    except:
        return False

    Debug( 'Writing Configuration Details...', True)
    config = ConfigParser.RawConfigParser()
    config.add_section('Twitter Account')
    config.set('Twitter Account', 'key', twitter_key)
    config.set('Twitter Account', 'secret', twitter_secret)            
    configfile = file(RESOURCE_PATH + '\settings.cfg', 'wb')
    config.write(configfile)
    Debug( '::StartOAuthProcess::', True)
    return CreateAPIObject()   

def VerifyAPIObject():
    Debug( '::VerifyAPIObject::', True)
    try:
        public_tweets = api.public_timeline()
        for tweet in public_tweets:
            pass
        bTwitterAPIVerified = True
        return True
    except:
        Debug( 'Exception: ' + str(sys.exc_info()[1]), True)
        return False
    Debug( '::VerifyAPIObject::', True)

def SetAutoStart(bState = True):
    Debug( '::AutoStart::', True)
    if (os.path.exists(AUTOEXEC_PATH)):
        Debug( 'Found Autoexec.py file, checking we''re there', True)
        bFound = False
        autoexecfile = file(AUTOEXEC_PATH, 'r')
        filecontents = autoexecfile.read()
        autoexecfile.seek(0)
        while 1:
            lines = autoexecfile.readlines(1000)
            if not lines: break
            for line in lines:
                if (string.find(line, 'xbtweet') > 1):
                    Debug( 'Found our script, no need to do anything', True)
                    bFound = True
        autoexecfile.close()
        if (not bFound):
            Debug( 'Appending our script to the autoexec.py script', True)
            autoexecfile = file(AUTOEXEC_PATH, 'w')
            autoexecfile.write (filecontents + '\r\n' + AUTOEXEC_SCRIPT)
            autoexecfile.close()
    else:
        Debug( 'File Autoexec.py is missing, creating file with autostart script', True)
        autoexecfile = file(AUTOEXEC_PATH, 'w')
        autoexecfile.write (AUTOEXEC_SCRIPT)
        autoexecfile.close()
    Debug( '::AutoStart::'  , True)


def UpdateStatus(update):
    global lasttweet
    if (update != lasttweet):
        lasttweet  = update        
        Debug ('Tweet: ' + update, False)
        api = CreateAPIObject()        
        update = api.update_status(update)

def CheckIfPlayingAndTweet_Video():
    if xbmc.Player().isPlayingVideo():
        Debug( 'Tweeting Video...', True)
        global CustomTweet_TVShow
        global CustomTweet_Movie        
        if len(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")) > 1: # TvShow
            title = CustomTweet_TVShow            
            title = title.replace('%SHOWNAME%', xbmc.getInfoLabel("VideoPlayer.TvShowTitle"))
            title = title.replace('%EPISODENAME%', xbmc.getInfoLabel("VideoPlayer.Title"))             
        elif len(xbmc.getInfoLabel("VideoPlayer.Title")) > 1: #Movie
            title = CustomTweet_Movie                       
            title = title.replace('%MOVIETITLE%', xbmc.getInfoLabel("VideoPlayer.Title"))
            title = title.replace('%MOVIEYEAR%', xbmc.getInfoLabel("VideoPlayer.Year"))
            #don't tweet if not in library
            if (xbmc.getInfoLabel("VideoPlayer.Year") == ""):
                title = ""

        if (title != ""):
            #Debug( 'Tweeting - ' + title, True)
            #Debug( xbmc.getInfoLabel("VideoPlayer.Time"), True)
            #Debug( xbmc.getInfoLabel("VideoPlayer.TimeRemaining"), True)
            #Debug( xbmc.getInfoLabel("VideoPlayer.Duration")    , True)                         
            UpdateStatus(title)

def CheckIfPlayingAndTweet_Music():
    if xbmc.Player().isPlayingAudio():
        global CustomTweet_Music
        Debug( 'Tweeting Music...', True) 
        title = CustomTweet_Music
        if len(xbmc.getInfoLabel("MusicPlayer.Title")) > 1: # Song
            title = title.replace('%ARTISTNAME%', xbmc.getInfoLabel("MusicPlayer.Artist"))
            title = title.replace('%SONGTITLE%', xbmc.getInfoLabel("MusicPlayer.Title"))
            title = title.replace('%ALBUMTITLE%', xbmc.getInfoLabel("MusicPlayer.Album"))            

        if (title != ""):
            #Debug( 'Tweeting - ' + title, True) 
            UpdateStatus(title)
            
#General vars
bRun = True #Enter idle state waiting to tweet
lasttweet = ""

#Twitter API related vars
bTwitterAccountDetailsSet = False
bTwitterAPIVerified = False

#Consts
AUTOEXEC_SCRIPT = 'import time\r\ntime.sleep(5)\r\nxbmc.executebuiltin("XBMC.RunScript(special://home/scripts/xbtweet/default.py,-startup)")' 

#Path handling
RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources' ) )
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib' ) )
CONFIG_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources' ) ) + '\settings.cfg'
AUTOEXEC_PATH = xbmc.translatePath( 'special://home/scripts/' ) + 'Autoexec.py'
sys.path.append (BASE_RESOURCE_PATH)

#Lib for Python Twitter
from tweepy import *

#Settings related parsing
__language__ = xbmc.Language( os.getcwd() ).getLocalizedString
_ = sys.modules[ "__main__" ].__language__
__settings__ = xbmc.Settings( path=os.getcwd() )

Debug('----------- ' + __scriptname__ + ' by ' + __author__ + ', version ' + __version__ + ' -----------', False)


username = __settings__.getSetting( "Username" )
password = __settings__.getSetting( "Password" )
bOAuth = __settings__.getSetting( "OAuth" )
if (bOAuth == 'true'):
    bOAuth = True
else:
    bOAuth = False
bAutoStart = __settings__.getSetting( "AutoStart" )
if (bAutoStart == 'true'):
    bAutoStart = True
else:
    bAutoStart = False
bFirstRun = CheckIfFirstRun()
bStartup = False
bCustomTweets = __settings__.getSetting( "CustomTweet" )
if (bCustomTweets == 'true'):
    bCustomTweets = True
else:
    bCustomTweets = False
CustomTweet_TVShow = __settings__.getSetting( "TVShowTweet" )
CustomTweet_Movie = __settings__.getSetting( "MovieTweet" )
CustomTweet_Music = __settings__.getSetting( "MusicTweet" )
    

Debug( '::Settings::', True)
Debug( 'AutoStart: ' + str(bAutoStart), True)
Debug( 'OAuth: ' + str(bOAuth), True)
Debug( 'Username: ' + username, True)
Debug( 'Password: ' + password, True)
Debug( 'FirstRun: ' + str(bFirstRun), True)
Debug( 'CustomTweets: ' + str(bCustomTweets), True)
Debug( 'CustomTweet_TVShow: ' + CustomTweet_TVShow, True)
Debug( 'CustomTweet_Movie: ' + CustomTweet_Movie, True)
Debug( 'CustomTweet_Music: ' + CustomTweet_Music, True)

try:
    count = len(sys.argv) - 1
    if (sys.argv[1] == '-startup'):
        bStartup = True
except:
    pass
Debug( 'Startup: ' + str(bStartup), True)
Debug( '::Settings::', True)

##
if __settings__.getSetting( "new_ver" ) == "true":
    import re
    import urllib
    #if not xbmc.getCondVisibility('Player.Paused') : xbmc.Player().pause() #Pause if not paused	
    usock = urllib.urlopen(__svn_url__ + "/default.py")
    htmlSource = usock.read()
    usock.close()

    version = re.search( "__version__.*?[\"'](.*?)[\"']",  htmlSource, re.IGNORECASE ).group(1)
    print "SVN Latest Version :[ "+version+"]"
    
    if version > __version__:
            import xbmcgui
            dialog = xbmcgui.Dialog()
            
            selected = dialog.ok("xbTweet v" + str(__version__), "Version "+ str(version)+ " of xbTweet is available" ,"Please use SVN repo Installer or XBMC zone Installer to update " )

##

FirstTimeMessageOAuth = "Please approve xbTwitter on the following screen."
FirstTimeMessagePlainAuth = "Please set Twitter account credentials\r\nin the scrip't settings."
PlainAuthIssues = "xbTwitter failed to authenticate you.\r\nPlease check the script's settings"
OAuthIssues = "xbTwitter failed to authenticate you.\r\nPlease approve xbTwitter on the following screen."

#Autoexec manipulation if set to AutoStart
if (not bStartup):
    SetAutoStart(bAutoStart)

if (bool(CreateAPIObject())):
    Debug( 'Twitter API object created successfully', True)
else:
    Debug( 'Failed to create Twitter API object', True)
    if (bFirstRun and bOAuth):
        dialog = xbmcgui.Dialog()
        dialog.ok("Welcome to xbTwitter", FirstTimeMessageOAuth)
        StartOAuthProcess()
    elif (not bFirstRun and bOAuth):
        dialog = xbmcgui.Dialog()
        dialog.ok("xbTwitter", OAuthIssues)        
        StartOAuthProcess()
    elif (bFirstRun and not bOAuth):
        dialog = xbmcgui.Dialog()
        dialog.ok("Welcome to xbTwitter", FirstTimeMessagePlainAuth)
        bRun = False
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok("xbTwitter", PlainAuthIssues)
        bRun = False

if (VerifyAPIObject()):
    Debug( 'Twitter API object verified', True)
else:
    Debug( 'Failed to verify Twitter API object', True)
    if (bOAuth):
        dialog = xbmcgui.Dialog()
        dialog.ok("xbTwitter", OAuthIssues)        
        StartOAuthProcess()
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok("xbTwitter", PlainAuthIssues)
        bRun = False

lasttweet = ""

if (bAutoStart and bStartup) or (not bStartup):
    Debug(  'Entering idle state, waiting for media playing...', False)
    while (bRun):
        #If Set To AutoTweet
        
        if __settings__.getSetting( "AutoTweetViedo" ) == "true":
            CheckIfPlayingAndTweet_Video()
        if __settings__.getSetting( "AutoTweetMusic" ) == "true":
            CheckIfPlayingAndTweet_Music()
        time.sleep(10)
