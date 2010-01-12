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
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/scripts/xbTweet/"
__credits__ = ""
__version__ = "0.0.892"
__XBMC_Revision__ = ""
   
def CheckIfPlayingAndTweet_Video(Manual=False):
    sType = ""
    if xbmc.Player().isPlayingVideo():
        Debug( 'Video is playing, checking if tweet is needed...', True)
        bLibraryExcluded = False
        bRatingExcluded = False
        bPathExcluded = False
        bExcluded = False
        short = ""
        title = ""
        global CustomTweet_TVShow
        global CustomTweet_Movie
        global VideoThreshold
        global TagsTweet
        global lasttitle
        global MAX_TWEET_LENGTH
        
        if ((xbmc.getInfoLabel("VideoPlayer.Year") == "") and __settings__.getSetting( "OnlyLibrary" ) == 'true'):
            Debug('Movie is not in library', False)
            bLibraryExcluded = True
        if ((xbmc.getInfoLabel("VideoPlayer.mpaa") == "XXX") and __settings__.getSetting( "ExcludeAdult" ) == 'true'):
            Debug('Movie is with XXX mpaa rating', False)            
            bRatingExcluded = True
        if ((__settings__.getSetting( "ExcludePath" ) != "") and (__settings__.getSetting( "ExcludePathOption" ) == 'true')):
            currentPath = xbmc.Player().getPlayingFile()
            if (currentPath.find(__settings__.getSetting( "ExcludePath" )) > -1):
                Debug('Movie is located in excluded path', False) 
                bPathExcluded = True
        
        if len(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")) >= 1: # TvShow
            sType = "TVShow"
            title = unicode(CustomTweet_TVShow , 'utf-8')           
            title = title.replace('%SHOWNAME%', unicode(xbmc.getInfoLabel("VideoPlayer.TvShowTitle"), 'utf-8'))
            title = title.replace('%EPISODENAME%', unicode(xbmc.getInfoLabel("VideoPlayer.Title"), 'utf-8'))
            title = title.replace('%SEASON%', unicode(xbmc.getInfoLabel("VideoPlayer.Season"), 'utf-8'))

            if (__settings__.getSetting( "AddBitly" ) == 'true'):
                imdburl = "http://www.tv.com/search.php?qs=" + xbmc.getInfoLabel("VideoPlayer.TvShowTitle") + ' ' + xbmc.getInfoLabel("VideoPlayer.Title")

        elif len(xbmc.getInfoLabel("VideoPlayer.Title")) >= 1: #Movie
            sType = "Movie"
            title = unicode(CustomTweet_Movie, 'utf-8')
            title = title.replace('%MOVIETITLE%', unicode(xbmc.getInfoLabel("VideoPlayer.Title"), 'utf-8'))
            title = title.replace('%MOVIEYEAR%', unicode(xbmc.getInfoLabel("VideoPlayer.Year"), 'utf-8'))

            if (xbmc.getInfoLabel("VideoPlayer.Year") != "") and (__settings__.getSetting( "AddBitly" ) == 'true'):
                imdburl = "www.imdb.com/find?s=all&q=" + xbmc.getInfoLabel("VideoPlayer.Title") + ' (' + xbmc.getInfoLabel("VideoPlayer.Year") + ')'
            
            #don't tweet if not in library
            if (xbmc.getInfoLabel("VideoPlayer.Year") == ""):
                title = ""

        if (bLibraryExcluded or bPathExcluded or bRatingExcluded):
            bExcluded = True
            
        if (((title != "" and lasttitle != title) or Manual) and not bExcluded):
            iPercComp = CalcPercentageRemaining(xbmc.getInfoLabel("VideoPlayer.Time"), xbmc.getInfoLabel("VideoPlayer.Duration"))
            if ((iPercComp > (float(VideoThreshold) / 100)) or Manual):
                lasttitle = title
                try:
                    bitlyAPI = Api(login="mrkav",apikey="R_f346d82149f7ae7fc8d2ee62d2854a56")
                    short = bitlyAPI.shorten(imdburl)    
                    Debug( "bit.ly URL = %s" % short, False)            
                except:
                    short = ""
                    pass
                if (short != ""):
                    if len(title + ' ' + short) <= MAX_TWEET_LENGTH: 
                        title = title + ' ' + short
                if len (title + ' ' + TagsTweet) <= MAX_TWEET_LENGTH:
                    title = title + ' ' + TagsTweet
                Debug('Title: ' + title + ' current percentage: ' + str(iPercComp), True)
                UpdateStatus(title, Manual)
                           

def CheckIfPlayingAndTweet_Music(Manual=False):
    if xbmc.Player().isPlayingAudio():
        global CustomTweet_Music
        global MusicThreshold
        global TagsTweet
        global lasttitle
        global MAX_TWEET_LENGTH
        
        Debug( 'Music is playing, checking if tweet is needed...', True) 
        title = unicode(CustomTweet_Music, 'utf-8')
        if len(xbmc.getInfoLabel("MusicPlayer.Title")) >= 1: # Song
            title = title.replace('%ARTISTNAME%', unicode(xbmc.getInfoLabel("MusicPlayer.Artist"), 'utf-8'))
            title = title.replace('%SONGTITLE%', unicode(xbmc.getInfoLabel("MusicPlayer.Title"), 'utf-8'))
            title = title.replace('%ALBUMTITLE%', unicode(xbmc.getInfoLabel("MusicPlayer.Album"), 'utf-8'))
            if (__settings__.getSetting( "AddBitly" ) == 'true'):
                imdburl = "http://www.last.fm/search?type=album&q=" + xbmc.getInfoLabel("MusicPlayer.Album")

        if len(title) > MAX_TWEET_LENGTH:
            title = title[1:MAX_TWEET_LENGTH]
        if ((title != "" and lasttitle != title) or Manual):
            iPercComp = CalcPercentageRemaining(xbmc.getInfoLabel("MusicPlayer.Time"), xbmc.getInfoLabel("MusicPlayer.Duration"))
            if ((iPercComp > (float(MusicThreshold) / 100)) or Manual):
                lasttitle = title                
                try:
                    bitlyAPI = Api(login="mrkav",apikey="R_f346d82149f7ae7fc8d2ee62d2854a56")
                    short = bitlyAPI.shorten(imdburl)    
                    Debug( "bit.ly URL = %s" % short, False)            
                except:
                    short = ""
                    pass
                if (short != ""):
                    if len(title + ' ' + short) <= MAX_TWEET_LENGTH: 
                        title = title + ' ' + short
                if len (title + ' ' + TagsTweet) <= MAX_TWEET_LENGTH:
                    title = title + ' ' + TagsTweet
                Debug('Title: ' + title + ' current percentage: ' + str(iPercComp), True)                
                UpdateStatus(title, Manual)
            

#Path handling
RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources' ) )
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'lib' ) )
LANGUAGE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'language' ) )
MEDIA_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'skins' ) )
sys.path.append (BASE_RESOURCE_PATH)
sys.path.append (LANGUAGE_RESOURCE_PATH)

from utilities import *
from twitter_wrapper import *
from bitly import *

Debug('----------- ' + __scriptname__ + ' by ' + __author__ + ', version ' + __version__ + ' -----------', False)

#Settings related parsing
__language__ = xbmc.Language( os.getcwd() ).getLocalizedString
_ = sys.modules[ "__main__" ].__language__
__settings__ = xbmc.Settings( path=os.getcwd() )

#Vars and initial load
MAX_TWEET_LENGTH = 140
bRun = True #Enter idle state waiting to tweet
bStartup = False
bShortcut = False
lasttitle = ""

bOAuth = False
bAutoStart = False
bRunBackground = False
bAutoTweetVideo = False
bAutoTweetMusic = False
bCustomTweets = False
CustomTweet_TVShow = ""
CustomTweet_Movie = ""
CustomTweet_Music = ""
TagsTweet = ""
VideoThreshold = 0
MusicThreshold = 0
FollowAuthor = False

if (__settings__.getSetting( "OAuth" ) == 'true'): bOAuth = True
if (__settings__.getSetting( "AutoStart" ) == 'true'): bAutoStart = True
if (__settings__.getSetting( "RunBackground" ) == 'true'): bRunBackground = True
if (__settings__.getSetting( "AutoTweetVideo" ) == 'true'): bAutoTweetVideo = True
if (__settings__.getSetting( "AutoTweetMusic" ) == 'true'): bAutoTweetMusic = True
if (__settings__.getSetting( "CustomTweet" ) == 'true'): bCustomTweets = True
if (__settings__.getSetting( "FollowAuthor" ) == 'true'): FollowAuthor = True
CustomTweet_TVShow = __settings__.getSetting( "TVShowTweet" )
CustomTweet_Movie = __settings__.getSetting( "MovieTweet" )
CustomTweet_Music = __settings__.getSetting( "MusicTweet" )
TagsTweet = __settings__.getSetting( "TagsTweet" )
VideoThreshold = int(__settings__.getSetting( "VideoThreshold" ))
if (VideoThreshold == 0): VideoThreshold = 1
elif (VideoThreshold == 1): VideoThreshold = 5
elif (VideoThreshold == 2): VideoThreshold = 15
elif (VideoThreshold == 3): VideoThreshold = 50
elif (VideoThreshold == 4): VideoThreshold = 75
elif (VideoThreshold == 5): VideoThreshold = 95
MusicThreshold = int(__settings__.getSetting( "MusicThreshold" ))
if (MusicThreshold == 0): MusicThreshold = 1
elif (MusicThreshold == 1): MusicThreshold = 5
elif (MusicThreshold == 2): MusicThreshold = 15
elif (MusicThreshold == 3): MusicThreshold = 50
elif (MusicThreshold == 4): MusicThreshold = 75
elif (MusicThreshold == 5): MusicThreshold = 95
bFirstRun = CheckIfFirstRun()
try:
    count = len(sys.argv) - 1
    if (sys.argv[1] == '-startup'):
        bStartup = True
    if (sys.argv[1] == '-shortcut'):
        bShortcut = True        
except:
    pass

Debug( '::Settings::', True)
Debug( 'AutoStart: ' + str(bAutoStart), True)
Debug( 'RunBackground: ' + str(bRunBackground), True)
Debug( 'OAuth: ' + str(bOAuth), True)
Debug( 'Username: ' + username, True)
Debug( 'Password: ' + password, True)
Debug( 'FirstRun: ' + str(bFirstRun), True)
Debug( 'AutoTweetViedo:' + str(bAutoTweetVideo), True)
Debug( 'AutoTweetMusic:' + str(bAutoTweetMusic), True)
Debug( 'CustomTweets: ' + str(bCustomTweets), True)
Debug( 'CustomTweet_TVShow: ' + unicode(CustomTweet_TVShow, 'utf-8'), True)
Debug( 'CustomTweet_Movie: ' + unicode(CustomTweet_Movie, 'utf-8'), True)
Debug( 'CustomTweet_Music: ' + unicode(CustomTweet_Music, 'utf-8'), True)
Debug( 'TagsTweet: ' + TagsTweet, True)
Debug( 'VideoThreshold: ' + str(VideoThreshold), True)
Debug( 'MusicThreshold: ' + str(MusicThreshold), True)
Debug( 'FollowAuthor: ' + str(FollowAuthor), True)
Debug( 'Startup: ' + str(bStartup), True)
Debug( 'Shortcut: ' + str(bShortcut), True)
Debug( '::Settings::', True)

if (CheckVersion() != __version__):
    import xbmcgui
    dialog = xbmcgui.Dialog()    
    selected = dialog.ok(__language__(30002) % (str(__version__)), __language__(30040), __language__(30041) )

    bRun = False
    WriteVersion(__version__)

if (not xbmc.getCondVisibility('videoplayer.isfullscreen') and not bShortcut and not bStartup):
    Debug(  'Pressed in scripts menu', False)        
    SetAutoStart(bAutoStart)
    if (FollowAuthor and bFirstRun):
        Debug('Following itayw', True)
        try:
            api = CreateAPIObject()        
            api.create_friendship('itayw')
        except:
            Debug('Failed to follow itayw', True)

if (not bRunBackground): bRun = False
if (bShortcut): bRun = False

#Startup Execution 
if ((bStartup and bAutoStart) or bRun):
    Debug(  'Entering idle state, waiting for media playing...', False)
    while 1:
        #If Set To AutoTweet
        if (bAutoTweetVideo):
            CheckIfPlayingAndTweet_Video()
        if (bAutoTweetMusic):
            CheckIfPlayingAndTweet_Music()
        time.sleep(5)
#Manual Execution - Skin or Shortcut
else:
    bManual = True
    Debug('Entering Manual Mode', False)
    #manual tweet
    if not xbmc.getCondVisibility('Player.Paused'): xbmc.Player().pause()
    CheckIfPlayingAndTweet_Video(True)
    CheckIfPlayingAndTweet_Music(True)
    if xbmc.getCondVisibility('Player.Paused'): xbmc.Player().pause()

Debug( 'Exiting...', False)
