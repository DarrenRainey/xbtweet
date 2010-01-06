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
__url__ = "http://www.xbmcblog.com/xbTweet"
__svn_url__ = "http://xbtweet.googlecode.com/svn/trunk/xbTweet/"
__credits__ = ""
__version__ = "0.0.846"
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

def VerifyAPIObject(api):
    Debug( '::VerifyAPIObject::', True)
    try:
        home_timeline = api.home_timeline()
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

def CalcPercentageRemaining(currenttime, duration):
    iCurrentMinutes = (int(currenttime.split(':')[0]) * 60) + int(currenttime.split(':')[1])
    iDurationMinutes = (int(duration.split(':')[0]) * 60) + int(duration.split(':')[1])
    return float(iCurrentMinutes) / float(iDurationMinutes) 

def UpdateStatus(update, Manual=False):
    global lasttweet

    if (Manual):
        keyboard = xbmc.Keyboard(update,'Enter Tweet')
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            update = keyboard.getText()
        else:
            return False
    
    if (update != lasttweet):
        lasttweet  = update        
        Debug ('Tweet: ' + update, False)
        api = CreateAPIObject()
        if (VerifyAPIObject(api)):
            update = api.update_status(update)
        else:
            print 'failed'

def CheckIfPlayingAndTweet_Video(Manual=False):
    sType = ""
    if xbmc.Player().isPlayingVideo():
        Debug( 'Tweeting Video...', True)
        global CustomTweet_TVShow
        global CustomTweet_Movie
        global VideoThreshold
        if len(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")) > 1: # TvShow
            sType = "TVShow"
            title = CustomTweet_TVShow            
            title = title.replace('%SHOWNAME%', xbmc.getInfoLabel("VideoPlayer.TvShowTitle"))
            title = title.replace('%EPISODENAME%', xbmc.getInfoLabel("VideoPlayer.Title"))             
        elif len(xbmc.getInfoLabel("VideoPlayer.Title")) > 1: #Movie
            sType = "Movie"
            title = CustomTweet_Movie                       
            title = title.replace('%MOVIETITLE%', xbmc.getInfoLabel("VideoPlayer.Title"))
            title = title.replace('%MOVIEYEAR%', xbmc.getInfoLabel("VideoPlayer.Year"))
            #don't tweet if not in library
            if (xbmc.getInfoLabel("VideoPlayer.Year") == ""):
                title = ""

        if ((title != "") or Manual):
            iPercComp = CalcPercentageRemaining(xbmc.getInfoLabel("VideoPlayer.Time"), xbmc.getInfoLabel("VideoPlayer.Duration"))
            Debug('Title: ' + title + ' current percentage: ' + str(iPercComp), True)
            if ((iPercComp > (VideoThreshold / 100)) or Manual):
                UpdateStatus(title, Manual)

def CheckIfPlayingAndTweet_Music(Manual=False):
    if xbmc.Player().isPlayingAudio():
        global CustomTweet_Music
        global MusicThreshold
        Debug( 'Tweeting Music...', True) 
        title = CustomTweet_Music
        if len(xbmc.getInfoLabel("MusicPlayer.Title")) > 1: # Song
            title = title.replace('%ARTISTNAME%', xbmc.getInfoLabel("MusicPlayer.Artist"))
            title = title.replace('%SONGTITLE%', xbmc.getInfoLabel("MusicPlayer.Title"))
            title = title.replace('%ALBUMTITLE%', xbmc.getInfoLabel("MusicPlayer.Album"))            

        if ((title != "") or Manual):
            iPercComp = CalcPercentageRemaining(xbmc.getInfoLabel("MusicPlayer.Time"), xbmc.getInfoLabel("MusicPlayer.Duration"))
            Debug('Title: ' + title + ' current percentage: ' + str(iPercComp), True)
            if ((iPercComp > (MusicThreshold / 100)) or Manual):
                UpdateStatus(title, Manual)
            
#General vars
bRun = True #Enter idle state waiting to tweet
lasttweet = ""

#Twitter API related vars
bTwitterAccountDetailsSet = False
bTwitterAPIVerified = False
 
#Consts
AUTOEXEC_SCRIPT = 'import time;time.sleep(5);xbmc.executebuiltin("XBMC.RunScript(special://home/scripts/xbtweet/default.py,-startup)")' 

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

bAutoTweetVideo = __settings__.getSetting( "AutoTweetVideo" )
if (bAutoTweetVideo == 'true'):
    bAutoTweetVideo = True
else:
    bAutoTweetVideo = False
bAutoTweetMusic = __settings__.getSetting( "AutoTweetMusic" )
if (bAutoTweetMusic == 'true'):
    bAutoTweetMusic = True
else:
    bAutoTweetMusic = False
VideoThreshold = int(__settings__.getSetting( "VideoThreshold" ))
if (VideoThreshold == 0):
    VideoThreshold = 1
elif (VideoThreshold == 1):
    VideoThreshold = 5
elif (VideoThreshold == 2):
    VideoThreshold = 15
elif (VideoThreshold == 3):
    VideoThreshold = 50
elif (VideoThreshold == 4):
    VideoThreshold = 75
elif (VideoThreshold == 5):
    VideoThreshold = 95
    
MusicThreshold = int(__settings__.getSetting( "MusicThreshold" ))
if (MusicThreshold == 0):
    MusicThreshold = 1
elif (MusicThreshold == 1):
    MusicThreshold = 5
elif (MusicThreshold == 2):
    MusicThreshold = 15
elif (MusicThreshold == 3):
    MusicThreshold = 50
elif (MusicThreshold == 4):
    MusicThreshold = 75
elif (MusicThreshold == 5):
    MusicThreshold = 95

FollowAuthor = __settings__.getSetting( "FollowAuthor" )
if (FollowAuthor == 'true'):
    FollowAuthor = True
else:
    FollowAuthor = False

Debug( '::Settings::', True)
Debug( 'AutoStart: ' + str(bAutoStart), True)
Debug( 'OAuth: ' + str(bOAuth), True)
Debug( 'Username: ' + username, True)
Debug( 'Password: ' + password, True)
Debug( 'FirstRun: ' + str(bFirstRun), True)
Debug( 'AutoTweetViedo:' + str(bAutoTweetVideo), True)
Debug( 'AutoTweetMusic:' + str(bAutoTweetMusic), True)
Debug( 'CustomTweets: ' + str(bCustomTweets), True)
Debug( 'CustomTweet_TVShow: ' + CustomTweet_TVShow, True)
Debug( 'CustomTweet_Movie: ' + CustomTweet_Movie, True)
Debug( 'CustomTweet_Music: ' + CustomTweet_Music, True)
Debug( 'VideoThreshold: ' + str(VideoThreshold), True)
Debug( 'MusicThreshold: ' + str(MusicThreshold), True)
Debug( 'FollowAuthor: ' + str(FollowAuthor), True)
try:
    count = len(sys.argv) - 1
    if (sys.argv[1] == '-startup'):
        bStartup = True
except:
    pass
Debug( 'Startup: ' + str(bStartup), True)
Debug( '::Settings::', True)

#Check for new version
if __settings__.getSetting( "new_ver" ) == "true":
    try:
        import re
        import urllib
        if not xbmc.getCondVisibility('Player.Paused') : xbmc.Player().pause() #Pause if not paused	
        usock = urllib.urlopen(__svn_url__ + "/default.py")
        htmlSource = usock.read()
        usock.close()

        version = re.search( "__version__.*?[\"'](.*?)[\"']",  htmlSource, re.IGNORECASE ).group(1)
        Debug ( "SVN Latest Version :[ "+version+"]", True)
        
        if version > __version__:
            import xbmcgui
            dialog = xbmcgui.Dialog()
            selected = dialog.ok("xbTweet v" + str(__version__), "Version "+ str(version)+ " of xbTweet is available" ,"Please check xbmcblog.com for more information" )
    except:
        print 'Exception in reading SVN'
        
FirstTimeMessageOAuth = "Please approve xbTwitter on the following screen."
FirstTimeMessagePlainAuth = "Please set Twitter account credentials\r\nin the scrip't settings."
PlainAuthIssues = "xbTwitter failed to authenticate you.\r\nPlease check the script's settings"
OAuthIssues = "xbTwitter failed to authenticate you.\r\nPlease approve xbTwitter on the following screen."

api = CreateAPIObject()
if (bool(api)):
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

if (VerifyAPIObject(api)):
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

if not xbmc.getCondVisibility('videoplayer.isfullscreen'):
    #Autoexec manipulation if set to AutoStart
    if (not bStartup):
        SetAutoStart(bAutoStart)
    if (FollowAuthor and bFirstRun):
        Debug('Following itayw', True)
        try:
            api = CreateAPIObject()        
            api.create_friendship('itayw')
        except:
            Debug('Failed to follow itayw', True)

    if (bAutoStart and bStartup) or (not bStartup):
        if (bRun):
            Debug(  'Entering idle state, waiting for media playing...', False)
            while (bRun):
                #If Set To AutoTweet
                if (bAutoTweetVideo):
                    CheckIfPlayingAndTweet_Video()
                if (bAutoTweetMusic):
                    CheckIfPlayingAndTweet_Music()
                time.sleep(5)
else:
    bManual = True
    Debug('Entering Manual Mode', False)
    #manual tweet
    if not xbmc.getCondVisibility('Player.Paused'): xbmc.Player().pause()
    CheckIfPlayingAndTweet_Video(True)
    CheckIfPlayingAndTweet_Music(True)
    if xbmc.getCondVisibility('Player.Paused'): xbmc.Player().pause()
