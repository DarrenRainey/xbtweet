import sys
import os
import xbmc
import xbmcgui
import string
import webbrowser
import time
import ConfigParser
import string

###General vars
__scriptname__ = "xbtweet"
__author__ = "Itay Weinberger"
__url__ = "http://www.xbmcblog.com/xbTweet"
__svn_url__ = "http://xbmc-addons.googlecode.com/svn/trunk/scripts/xbTweet/"
__credits__ = ""
__version__ = "1.0.0"
__XBMC_Revision__ = ""

def addPadding(number):
    if len(number) == 1:
        number = '0' + number
    return number

def CheckIfPlayingAndTweet_Video(Manual=False):
    sType = ""
    if xbmc.Player().isPlayingVideo():
        bLibraryExcluded = False
        bRatingExcluded = False
        bPathExcluded = False
        bExcluded = False
        short = ""
        title = ""
        imdburl = ""
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
        if ((__settings__.getSetting( "ExcludePath2" ) != "") and (__settings__.getSetting( "ExcludePathOption2" ) == 'true')):
            currentPath = xbmc.Player().getPlayingFile()
            if (currentPath.find(__settings__.getSetting( "ExcludePath2" )) > -1):
                Debug('Movie is located in excluded path 2', False) 
                bPathExcluded = True
        if ((__settings__.getSetting( "ExcludePath3" ) != "") and (__settings__.getSetting( "ExcludePathOption3" ) == 'true')):
            currentPath = xbmc.Player().getPlayingFile()
            if (currentPath.find(__settings__.getSetting( "ExcludePath3" )) > -1):
                Debug('Movie is located in excluded path 3', False) 
                bPathExcluded = True                     
        
        if len(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")) >= 1: # TvShow
            sType = "TVShow"
            title = unicode(CustomTweet_TVShow , 'utf-8')           
            title = title.replace('%SHOWNAME%', unicode(xbmc.getInfoLabel("VideoPlayer.TvShowTitle"), 'utf-8'))
            title = title.replace('%EPISODENAME%', unicode(xbmc.getInfoLabel("VideoPlayer.Title"), 'utf-8'))
            title = title.replace('%EPISODENUMBER%', unicode(xbmc.getInfoLabel("VideoPlayer.Episode"), 'utf-8'))
            title = title.replace('%EPISODENUMBER_PADDED%', unicode(addPadding(xbmc.getInfoLabel("VideoPlayer.Episode")), 'utf-8'))            
            title = title.replace('%SEASON%', unicode(xbmc.getInfoLabel("VideoPlayer.Season"), 'utf-8'))
            title = title.replace('%SEASON_PADDED%', unicode(addPadding(xbmc.getInfoLabel("VideoPlayer.Season")), 'utf-8'))            

            if (__settings__.getSetting( "AddBitly" ) == 'true'):
                try:
                    query = "select case when not tvshow.c12 is null then tvshow.c12 else 'NOTFOUND' end as [ShowID] from tvshow where tvshow.c00 = '" + unicode(xbmc.getInfoLabel("VideoPlayer.TvShowTitle")) + "' limit 1"
                    res = xbmc.executehttpapi("queryvideodatabase(" + query + ")")
                    tvshowid = re.findall('>(.*?)<',res) # find it
                    if len(tvshowid[1].strip()) >= 1:
                        imdburl = "http://thetvdb.com/?tab=series&id=" + str(tvshowid[1].strip())
                except:        
                    imdburl = ""

        elif len(xbmc.getInfoLabel("VideoPlayer.Title")) >= 1: #Movie
            sType = "Movie"
            title = unicode(CustomTweet_Movie, 'utf-8')
            title = title.replace('%MOVIETITLE%', unicode(xbmc.getInfoLabel("VideoPlayer.Title"), 'utf-8'))
            title = title.replace('%MOVIEYEAR%', unicode(xbmc.getInfoLabel("VideoPlayer.Year"), 'utf-8'))

            if (xbmc.getInfoLabel("VideoPlayer.Year") != "") and (__settings__.getSetting( "AddBitly" ) == 'true'):
                try:
                    query = "select case when not movie.c09 is null then movie.c09 else 'NOTFOUND' end as [MovieID] from movie where movie.c00 = '" + unicode(xbmc.getInfoLabel("VideoPlayer.Title")) + "' limit 1"
                    res = xbmc.executehttpapi("queryvideodatabase(" + query + ")")
                    movieid = re.findall('>(.*?)<',res) # find it
                    if len(movieid[1].strip()) >= 1:
                        imdburl = "http://www.imdb.com/title/" + str(movieid[1].strip())
                except:        
                    imdburl = ""
                
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
                    Debug( "bit.ly URL = %s" % short, True)            
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
        
        #Debug( 'Music is playing, checking if tweet is needed...', True) 
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
                    Debug( "bit.ly URL = %s" % short, True)            
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

def ShowMessage(MessageID):    
    import gui_auth
    message = __language__(MessageID)
    ui = gui_auth.GUI( "script-xbTweet-Generic.xml" , os.getcwd(), "Default")
    ui.setParams ("message", __language__(30042), message, 0)
    ui.doModal()
    del ui
    
###Path handling
BASE_PATH = xbmc.translatePath( os.getcwd() )
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

###Settings related parsing
__language__ = xbmc.Language( os.getcwd() ).getLocalizedString
_ = sys.modules[ "__main__" ].__language__
__settings__ = xbmc.Settings( path=os.getcwd() )

###Vars and initial load
MAX_TWEET_LENGTH = 140
bRun = True #Enter idle state waiting to tweet
bStartup = False
bShortcut = False
lasttitle = ""

bOAuth = False
bUseAnotherAccount = False
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

bNotifyTimeline = False
bNotifyMention = False
bNotifyDirect = False

bShowWhatsNew = False

if (__settings__.getSetting( "OAuth" ) == 'true'): bOAuth = True
if (__settings__.getSetting( "UseAnotherAccount" ) == 'true'): bUseAnotherAccount = True

if (__settings__.getSetting( "AutoStart" ) == 'true'): bAutoStart = True
if (__settings__.getSetting( "RunBackground" ) == 'true'): bRunBackground = True
if (__settings__.getSetting( "AutoTweetVideo" ) == 'true'): bAutoTweetVideo = True
if (__settings__.getSetting( "AutoTweetMusic" ) == 'true'): bAutoTweetMusic = True
if (__settings__.getSetting( "CustomTweet" ) == 'true'): bCustomTweets = True
if (__settings__.getSetting( "FollowAuthor" ) == 'true'): FollowAuthor = True

if (__settings__.getSetting( "showwhatsnew" ) == 'true'): bShowWhatsNew = True

if (__settings__.getSetting( "NotifyTimeline" ) == 'true'): bNotifyTimeline = True
if (__settings__.getSetting( "NotifyMention" ) == 'true'): bNotifyMention = True
if (__settings__.getSetting( "NotifyDirect" ) == 'true'): bNotifyDirect = True
NotifyInterval = int(__settings__.getSetting( "NotifyInterval" ))
if (NotifyInterval == 0): NotifyInterval = 3
elif (NotifyInterval == 1): NotifyInterval = 5
elif (NotifyInterval == 2): NotifyInterval = 10
elif (NotifyInterval == 3): NotifyInterval = 60
elif (NotifyInterval == 4): NotifyInterval = 120
elif (NotifyInterval == 5): NotifyInterval = 180

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
Debug( 'NotifyInterval: ' + str(NotifyInterval), True)
Debug( 'ShowWhatsNew:' + str(bShowWhatsNew), True)
Debug( '::Settings::', True)

###Initial checks
#API Validation
api, auth = Twitter_Login()
if not api:
    ShowMessage(40007) #OAuth starts
    bRun = False

#New Version
if ((CheckVersion() != __version__ ) and (bShowWhatsNew)):
    try:
        import urllib
        usock = urllib.urlopen("http://xbtweet.googlecode.com/svn/trunk/xbTweet/whatsnew" + __version__ + ".txt")
        message = usock.read()
        usock.close()

        import gui_welcome
        ui = gui_welcome.GUI( "script-xbTweet-Generic.xml" , os.getcwd(), "Default")
        ui.setParams ("message",  __language__(30043), message, 0)
        ui.doModal()
        del ui

        #bRun = True
        WriteVersion(__version__)
    except:
        Debug('Failed to validate if new version', False)

###Main logic
if (not xbmc.getCondVisibility('videoplayer.isfullscreen') and not bShortcut and not bStartup):
    Debug(  'Pressed in scripts menu', False)        
    SetAutoStart(bAutoStart)
    if (FollowAuthor and bFirstRun):
        Debug('Following xbmcblog', True)
        try:
            api = CreateAPIObject()        
            api.create_friendship('xbmcblog')
        except:
            Debug('Failed to follow xbmcblog', True)

if (not bRunBackground): bRun = False
if (bShortcut): bRun = False

#Startup Execution 
if ((bStartup and bAutoStart) or bRun):
    Debug(  'Entering idle state, waiting for media playing...', False)

    twittersmallicon = xbmc.translatePath( os.path.join( MEDIA_RESOURCE_PATH, 'Default', 'media', 'smalltwitter.png' ) )
    xbmc.executebuiltin('Notification(xbTweet,' + __language__(30044).encode( "utf-8", "ignore" ) + ',3000,' + twittersmallicon + ')')
    
    #we need the last id
    lastid = 0
    lastDMid = 0
    lastTweetid = 0
    timeline_interval = 0
    newNotification = CheckForMentions(lastid)
    if newNotification != None:
        lastid = newNotification.id
    else:
        lastid = 0
    #lastid = 5832633350
    Debug('Last mention id: ' + str(lastid), True)

    newNotification = None
    newNotification = CheckForDM(lastDMid)
    if newNotification != None:
        lastDMid = newNotification.id
    else:
        lastDMid = 0
    #lastDMid = 754665490
    Debug('Last DM id: ' + str(lastDMid), True)

    newTweets = None
    newTweets = CheckForTimeline(lastTweetid)
    if newTweets != None:
        lastTweetid = newTweets[0].id
    else:
        lastTweetid = 0
    #lastTweetid = 11986090060
    Debug('Last Tweet id: ' + str(lastTweetid), True)    

    while 1:
        #If Set To AutoTweet
        if (bAutoTweetVideo):
            CheckIfPlayingAndTweet_Video()
        if (bAutoTweetMusic):
            CheckIfPlayingAndTweet_Music()
        #NotifyInterval = 0.5
        if ((timeline_interval * 5) % (NotifyInterval * 60) == 0):
            Debug('Notification Interval Reached...', False)
            timeline_interval = 0
            newNotification = ""
            newNotification = CheckForMentions(lastid)
            if (newNotification != None):
                lastid = newNotification.id
                if not xbmc.getCondVisibility('Player.Paused') : xbmc.Player().pause() #Pause if not paused
                import Window_Notification
                ui = Window_Notification.GUI( "script-xbTweet-Notification.xml" , BASE_PATH, "Default")
                ui.setTwitterText (newNotification.text, "mention", newNotification.user.screen_name, newNotification.user.profile_image_url, newNotification.created_at, newNotification.source)
                ui.doModal()
                if xbmc.getCondVisibility('Player.Paused'): xbmc.Player().pause() # if Paused, un-pause
                del ui

            newNotification = None
            newNotification = CheckForDM(lastDMid)
            if (newNotification != None):
                lastDMid = newNotification.id
                if not xbmc.getCondVisibility('Player.Paused') : xbmc.Player().pause() #Pause if not paused
                import Window_Notification
                ui = Window_Notification.GUI( "script-xbTweet-Notification.xml" , BASE_PATH, "Default")
                ui.setTwitterText (newNotification.text, "direct_message", newNotification.sender.screen_name, newNotification.sender.profile_image_url, newNotification.created_at, "")
                ui.doModal()
                if xbmc.getCondVisibility('Player.Paused'): xbmc.Player().pause() # if Paused, un-pause
                del ui

            newTweets = None
            newTweets = CheckForTimeline(lastTweetid)
            if (newTweets != None):
                #import Window_Fall
                counter = 0
                
                while (counter < len(newTweets)):
                    tweet = newTweets[counter]
                    import Window_Fall
                    ui = Window_Fall.GUI( "script-xbTweet-Fall.xml" , BASE_PATH, "Default", True)
                    ui.setTwitterText (tweet.text, "tweet", tweet.user.screen_name, tweet.user.profile_image_url, tweet.created_at, tweet.source, counter)
                    ui.show()
                    ui.onInit()
                    counter = counter + 1
                    time.sleep(0.1)                        
                lastTweetid = newTweets[counter-1].id
                #lastTweetid = 11986090060
                 
        timeline_interval = timeline_interval + 1
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
